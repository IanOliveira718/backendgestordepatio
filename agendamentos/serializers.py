from rest_framework import serializers
from .models import Agendamento, PalletDescricao, VolumeDescricao, Pallet

# Importa o model de Zona do app patio para verificar capacidade
try:
    from patio.models import Zona
    PATIO_APP_AVAILABLE = True
except ImportError:
    PATIO_APP_AVAILABLE = False


def get_tipo(user):
    try:
        return user.profile.tipo
    except Exception:
        return None

class PalletDescricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PalletDescricao
        fields = ["ordem", "descricao"]


class VolumeDescricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolumeDescricao
        fields = [
            "ordem",
            "descricao",
            "altura",
            "largura",
            "comprimento",
        ]


class PalletSerializer(serializers.ModelSerializer):

    agendamento_date = serializers.DateField(
        source="agendamento.date",
        read_only=True,
        format="%Y-%m-%d"
    )

    agendamento_time = serializers.TimeField(
        source="agendamento.time",
        read_only=True,
        format="%H:%M"
    )

    agendamento_plate = serializers.CharField(
        source="agendamento.plate",
        read_only=True
    )

    class Meta:
        model = Pallet

        fields = [
            "id",
            "agendamento",
            "agendamento_plate",
            "agendamento_date",
            "agendamento_time",
            "numero_pallet",
            "numero_espaco",
            "zona_nome",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class AtualizarStatusPalletSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Pallet.Status.choices
    )


class AgendamentoSerializer(serializers.ModelSerializer):

    id = serializers.CharField(
        source="pk",
        read_only=True
    )

    date = serializers.DateField(
        format="%Y-%m-%d"
    )

    time = serializers.TimeField(
        format="%H:%M"
    )

    # ✅ Sem source
    descricoes_pallets = PalletDescricaoSerializer(
        many=True,
        required=False,
        default=list
    )

    # ✅ Sem source
    descricoes_volumes = VolumeDescricaoSerializer(
        many=True,
        required=False,
        default=list
    )

    class Meta:
        model = Agendamento

        fields = [
            "id",
            "date",
            "time",
            "plate",
            "driver",
            "type",
            "zone",
            "pallets",
            "urgente",
            "nota_fiscal",
            "tipo_unidade",
            "descricoes_pallets",
            "descricoes_volumes",
            "status",
        ]

        read_only_fields = [
            "id",
            "status",
        ]

    def validate(self, data):
        date               = data.get("date")
        time               = data.get("time")
        zone               = data.get("zone")
        qtd_pallets        = data.get("pallets", 0)
        urgente            = data.get("urgente")
        tipo_unidade       = data.get("tipo_unidade", Agendamento.TipoUnidade.PALLET)
        descricoes_pallets = data.get("descricoes_pallets", [])
        descricoes_volumes = data.get("descricoes_volumes", [])
        request = self.context.get("request")
        
        # ── 1. Conflito de horário exato na mesma zona ────────────────────────
        conflito = Agendamento.objects.filter(
            date=date, time=time, zone=zone
        ).exclude(status=Agendamento.Status.CANCELADO)

        if self.instance:
            conflito = conflito.exclude(pk=self.instance.pk)

        if conflito.exists():
            raise serializers.ValidationError({
                "time": "Não foi possível agendar, já existe um agendamento nesse horário."
            })

        if urgente == 1:
            if not(request.user.is_authenticated and (get_tipo(request.user) in ("administrador","colaborador","meio_ambiente"))):
                raise serializers.ValidationError({"time": "Não foi possível agendar, você não pode fazer agendamentos urgentes."})

        # ── 2. Capacidade da zona com janela de tempo configurável ────────────
        try:
            from patio.models import Zona
            zona_obj = Zona.objects.get(nome=zone)

            from agendamentos.capacidade_validator import verificar_capacidade
            erro_capacidade = verificar_capacidade(
                zona_nome=zone,
                zona_capacidade=zona_obj.capacidade,
                qtd_pallets=qtd_pallets,
                data_agendamento=date,
                hora_agendamento=time,
                excluir_agendamento_id=self.instance.pk if self.instance else None,
            )
            if erro_capacidade:
                raise serializers.ValidationError({"pallets": erro_capacidade})

        except Zona.DoesNotExist:
            pass  # Zona não cadastrada no app patio — ignora validação de capacidade

        # ── 3. Descrições x quantidade ────────────────────────────────────────
        if tipo_unidade == Agendamento.TipoUnidade.PALLET:
            if len(descricoes_pallets) != qtd_pallets:
                raise serializers.ValidationError({
                    "descricoes_pallets": (
                        f"Informe exatamente {qtd_pallets} descrição(ões). "
                        f"Recebido: {len(descricoes_pallets)}."
                    )
                })
            ordens = sorted([d["ordem"] for d in descricoes_pallets])
            if ordens != list(range(1, qtd_pallets + 1)):
                raise serializers.ValidationError({
                    "descricoes_pallets": f"As ordens devem ser de 1 a {qtd_pallets} sem repetição."
                })
        elif tipo_unidade == Agendamento.TipoUnidade.VOLUME:
            if len(descricoes_volumes) != qtd_pallets:
                raise serializers.ValidationError({
                    "descricoes_volumes": (
                        f"Informe exatamente {qtd_pallets} descrição(ões). "
                        f"Recebido: {len(descricoes_volumes)}."
                    )
                })
            ordens = sorted([d["ordem"] for d in descricoes_volumes])
            if ordens != list(range(1, qtd_pallets + 1)):
                raise serializers.ValidationError({
                    "descricoes_volumes": f"As ordens devem ser de 1 a {qtd_pallets} sem repetição."
                })

        return data

    def _alocar_espacos(
        self,
        zona_nome,
        qtd
    ):

        ocupados = set(
            Pallet.objects.filter(
                zona_nome=zona_nome,
                status__in=[
                    Pallet.Status.PENDENTE,
                    Pallet.Status.ARMAZENADO,
                ],
            ).values_list(
                "numero_espaco",
                flat=True
            )
        )

        espacos = []
        candidato = 1

        while len(espacos) < qtd:

            if candidato not in ocupados:
                espacos.append(candidato)

            candidato += 1

        return espacos

    def create(self, validated_data):
        tipo_unidade       = validated_data.get("tipo_unidade", Agendamento.TipoUnidade.PALLET)
        descricoes_pallets = validated_data.pop("descricoes_pallets", [])
        descricoes_volumes = validated_data.pop("descricoes_volumes", [])
        zona_nome          = validated_data.get("zone")
        qtd                = validated_data.get("pallets", 0)
        urgente            = validated_data.get("urgente")

        # Salva quem criou o agendamento (usado para filtro do fornecedor)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["criado_por"] = request.user

        agendamento = Agendamento.objects.create(**validated_data)

        if tipo_unidade == Agendamento.TipoUnidade.PALLET:
            PalletDescricao.objects.bulk_create([
                PalletDescricao(agendamento=agendamento, **d)
                for d in descricoes_pallets
            ])
        else:
            VolumeDescricao.objects.bulk_create([
                VolumeDescricao(agendamento=agendamento, **d)
                for d in descricoes_volumes
            ])

        espacos = self._alocar_espacos(zona_nome, qtd)
        Pallet.objects.bulk_create([
            Pallet(
                agendamento=agendamento,
                numero_pallet=i + 1,
                numero_espaco=espacos[i],
                zona_nome=zona_nome,
                status=Pallet.Status.PENDENTE,
            )
            for i in range(qtd)
        ])

        return agendamento


class AgendamentoListSerializer(serializers.ModelSerializer):

    id = serializers.CharField(
        source="pk",
        read_only=True
    )

    date = serializers.DateField(
        format="%Y-%m-%d"
    )

    time = serializers.TimeField(
        format="%H:%M"
    )

    class Meta:

        model = Agendamento

        fields = [
            "id",
            "date",
            "time",
            "plate",
            "driver",
            "type",
            "zone",
            "pallets",
            "urgente",
            "nota_fiscal",
            "tipo_unidade",
            "status",
        ]


class AgendamentoDetailSerializer(
    serializers.ModelSerializer
):

    id = serializers.CharField(
        source="pk",
        read_only=True
    )

    date = serializers.DateField(
        format="%Y-%m-%d"
    )

    time = serializers.TimeField(
        format="%H:%M"
    )

    descricoes_pallets = (
        PalletDescricaoSerializer(
            many=True,
            read_only=True
        )
    )

    descricoes_volumes = (
        VolumeDescricaoSerializer(
            many=True,
            read_only=True
        )
    )

    # ✅ Aqui o source permanece
    pallets_detalhes = PalletSerializer(
        source="pallet_registrados",
        many=True,
        read_only=True
    )

    class Meta:

        model = Agendamento

        fields = [
            "id",
            "date",
            "time",
            "plate",
            "driver",
            "type",
            "zone",
            "pallets",
            "urgente",
            "nota_fiscal",
            "tipo_unidade",
            "descricoes_pallets",
            "descricoes_volumes",
            "pallets_detalhes",
            "status",
        ]


class AtualizarStatusSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=Agendamento.Status.choices
    )


class AgendamentoPorPeriodoSerializer(
    serializers.Serializer
):

    start_date = serializers.DateField()

    end_date = serializers.DateField()

    def validate(self, data):

        if data["start_date"] > data["end_date"]:

            raise serializers.ValidationError(
                "start_date não pode ser posterior a end_date."
            )

        return data