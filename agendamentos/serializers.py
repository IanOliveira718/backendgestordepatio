from rest_framework import serializers
from .models import Agendamento, PalletDescricao, VolumeDescricao, Pallet

# Importa o model de Zona do app patio para verificar capacidade
try:
    from patio.models import Zona
    PATIO_APP_AVAILABLE = True
except ImportError:
    PATIO_APP_AVAILABLE = False


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

        date = data.get("date")
        time = data.get("time")
        zone = data.get("zone")

        qtd_pallets = data.get("pallets", 0)

        tipo_unidade = data.get(
            "tipo_unidade",
            Agendamento.TipoUnidade.PALLET
        )

        descricoes_pallets = data.get(
            "descricoes_pallets",
            []
        )

        descricoes_volumes = data.get(
            "descricoes_volumes",
            []
        )

        # ─────────────────────────────────────────────
        # 1. Conflito de horário
        # ─────────────────────────────────────────────

        conflito = Agendamento.objects.filter(
            date=date,
            time=time,
            zone=zone
        ).exclude(
            status=Agendamento.Status.CANCELADO
        )

        if self.instance:
            conflito = conflito.exclude(
                pk=self.instance.pk
            )

        if conflito.exists():
            raise serializers.ValidationError({
                "time": (
                    "Não foi possível agendar, "
                    "já existe um agendamento nesse horário."
                )
            })

        # ─────────────────────────────────────────────
        # 2. Capacidade da zona
        # ─────────────────────────────────────────────

        if PATIO_APP_AVAILABLE:

            try:

                zona_obj = Zona.objects.get(
                    nome=zone
                )

                ocupados = Pallet.objects.filter(
                    zona_nome=zone,
                    status__in=[
                        Pallet.Status.PENDENTE,
                        Pallet.Status.ARMAZENADO,
                    ],
                ).count()

                disponiveis = (
                    zona_obj.capacidade - ocupados
                )

                if qtd_pallets > disponiveis:

                    raise serializers.ValidationError({
                        "pallets": (
                            f"A zona {zone} possui "
                            f"{disponiveis} espaço(s) disponível(is)."
                        )
                    })

            except Zona.DoesNotExist:
                pass

        # ─────────────────────────────────────────────
        # 3. Validação descrições
        # ─────────────────────────────────────────────

        if tipo_unidade == Agendamento.TipoUnidade.PALLET:

            if len(descricoes_pallets) != qtd_pallets:

                raise serializers.ValidationError({
                    "descricoes_pallets": (
                        f"Informe exatamente "
                        f"{qtd_pallets} descrição(ões)."
                    )
                })

            ordens = sorted([
                d["ordem"]
                for d in descricoes_pallets
            ])

            if ordens != list(
                range(1, qtd_pallets + 1)
            ):

                raise serializers.ValidationError({
                    "descricoes_pallets": (
                        f"As ordens devem ser "
                        f"de 1 até {qtd_pallets}."
                    )
                })

        elif tipo_unidade == Agendamento.TipoUnidade.VOLUME:

            if len(descricoes_volumes) != qtd_pallets:

                raise serializers.ValidationError({
                    "descricoes_volumes": (
                        f"Informe exatamente "
                        f"{qtd_pallets} descrição(ões)."
                    )
                })

            ordens = sorted([
                d["ordem"]
                for d in descricoes_volumes
            ])

            if ordens != list(
                range(1, qtd_pallets + 1)
            ):

                raise serializers.ValidationError({
                    "descricoes_volumes": (
                        f"As ordens devem ser "
                        f"de 1 até {qtd_pallets}."
                    )
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

        descricoes_pallets = validated_data.pop(
            "descricoes_pallets",
            []
        )

        descricoes_volumes = validated_data.pop(
            "descricoes_volumes",
            []
        )

        tipo_unidade = validated_data.get(
            "tipo_unidade",
            Agendamento.TipoUnidade.PALLET
        )

        zona_nome = validated_data.get(
            "zone"
        )

        qtd = validated_data.get(
            "pallets",
            0
        )

        agendamento = Agendamento.objects.create(
            **validated_data
        )

        # ─────────────────────────────────────────────
        # Cria descrições
        # ─────────────────────────────────────────────

        if tipo_unidade == Agendamento.TipoUnidade.PALLET:

            PalletDescricao.objects.bulk_create([
                PalletDescricao(
                    agendamento=agendamento,
                    **d
                )
                for d in descricoes_pallets
            ])

        else:

            VolumeDescricao.objects.bulk_create([
                VolumeDescricao(
                    agendamento=agendamento,
                    **d
                )
                for d in descricoes_volumes
            ])

        # ─────────────────────────────────────────────
        # Cria pallets automaticamente
        # ─────────────────────────────────────────────

        espacos = self._alocar_espacos(
            zona_nome,
            qtd
        )

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