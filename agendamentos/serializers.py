from rest_framework import serializers
from .models import Agendamento, PalletDescricao, VolumeDescricao


class PalletDescricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PalletDescricao
        fields = ["ordem", "descricao"]


class VolumeDescricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VolumeDescricao
        fields = ["ordem", "descricao", "altura", "largura", "comprimento"]

class AgendamentoDetailSerializer(serializers.ModelSerializer):
    id                 = serializers.CharField(source="pk", read_only=True)
    date               = serializers.DateField(format="%Y-%m-%d")
    time               = serializers.TimeField(format="%H:%M")
    descricoes_pallets = PalletDescricaoSerializer(many=True, read_only=True)
    descricoes_volumes = VolumeDescricaoSerializer(many=True, read_only=True)

    class Meta:
        model  = Agendamento
        fields = [
            "id", "date", "time", "plate", "driver", "type",
            "zone", "pallets", "nota_fiscal", "tipo_unidade",
            "descricoes_pallets", "descricoes_volumes", "status",
        ]

class AgendamentoSerializer(serializers.ModelSerializer):
    id                 = serializers.CharField(source="pk", read_only=True)
    date               = serializers.DateField(format="%Y-%m-%d")
    time               = serializers.TimeField(format="%H:%M")
    descricoes_pallets = PalletDescricaoSerializer(many=True, required=False, default=list)
    descricoes_volumes = VolumeDescricaoSerializer(many=True, required=False, default=list)

    class Meta:
        model  = Agendamento
        fields = [
            "id", "date", "time", "plate", "driver", "type",
            "zone", "pallets", "nota_fiscal", "tipo_unidade",
            "descricoes_pallets", "descricoes_volumes", "status",
        ]
        read_only_fields = ["id", "status"]

    def validate(self, data):
        tipo_unidade = data.get("tipo_unidade", Agendamento.TipoUnidade.PALLET)
        pallets      = data.get("pallets", 0)
        descricoes_pallets = data.get("descricoes_pallets", [])
        descricoes_volumes = data.get("descricoes_volumes", [])

        if tipo_unidade == Agendamento.TipoUnidade.PALLET:
            if len(descricoes_pallets) != pallets:
                raise serializers.ValidationError({
                    "descricoes_pallets": (
                        f"Informe exatamente {pallets} descrição(ões) de pallets. "
                        f"Recebido: {len(descricoes_pallets)}."
                    )
                })
            # Valida ordens sequenciais sem repetição
            ordens = sorted([d["ordem"] for d in descricoes_pallets])
            if ordens != list(range(1, pallets + 1)):
                raise serializers.ValidationError({
                    "descricoes_pallets": f"As ordens devem ser de 1 a {pallets} sem repetição."
                })

        elif tipo_unidade == Agendamento.TipoUnidade.VOLUME:
            if len(descricoes_volumes) != pallets:
                raise serializers.ValidationError({
                    "descricoes_volumes": (
                        f"Informe exatamente {pallets} descrição(ões) de volumes. "
                        f"Recebido: {len(descricoes_volumes)}."
                    )
                })
            ordens = sorted([d["ordem"] for d in descricoes_volumes])
            if ordens != list(range(1, pallets + 1)):
                raise serializers.ValidationError({
                    "descricoes_volumes": f"As ordens devem ser de 1 a {pallets} sem repetição."
                })

        return data

    def create(self, validated_data):
        tipo_unidade       = validated_data.get("tipo_unidade", Agendamento.TipoUnidade.PALLET)
        descricoes_pallets = validated_data.pop("descricoes_pallets", [])
        descricoes_volumes = validated_data.pop("descricoes_volumes", [])

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

        return agendamento


class AgendamentoListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagens — sem as descrições."""
    id   = serializers.CharField(source="pk", read_only=True)
    date = serializers.DateField(format="%Y-%m-%d")
    time = serializers.TimeField(format="%H:%M")

    class Meta:
        model  = Agendamento
        fields = [
            "id", "date", "time", "plate", "driver",
            "type", "zone", "pallets", "nota_fiscal",
            "tipo_unidade", "status",
        ]


class AtualizarStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Agendamento.Status.choices)


class AgendamentoPorPeriodoSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date   = serializers.DateField()

    def validate(self, data):
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError(
                "start_date não pode ser posterior a end_date."
            )
        return data
