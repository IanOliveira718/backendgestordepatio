from rest_framework import serializers
from .models import Agendamento, PalletDescricao


class PalletDescricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PalletDescricao
        fields = ["ordem", "descricao"]


class AgendamentoSerializer(serializers.ModelSerializer):

    descricoes_pallets = PalletDescricaoSerializer(many=True)

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
            "descricoes_pallets",
            "status",
        ]
        read_only_fields = ["id", "status"]

    def create(self, validated_data):
        descricoes = validated_data.pop("descricoes_pallets")

        agendamento = Agendamento.objects.create(**validated_data)

        for pallet in descricoes:
            PalletDescricao.objects.create(
                agendamento=agendamento,
                **pallet
            )

        return agendamento


class AtualizarStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Agendamento.Status.choices
    )


class AgendamentoPorPeriodoSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError(
                "start_date não pode ser posterior a end_date."
            )
        return data