from rest_framework import serializers
from .models import Agendamento


class AgendamentoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    date = serializers.DateField(format="%Y-%m-%d")
    time = serializers.TimeField(format="%H:%M")

    class Meta:
        model = Agendamento
        fields = ["id", "date", "time", "plate", "driver", "type", "zone", "pallets", "status"]
        read_only_fields = ["id", "status"]

    def validate_type(self, value):
        if value not in Agendamento.Tipo.values:
            raise serializers.ValidationError(
                f"Tipo inválido. Use: {', '.join(Agendamento.Tipo.values)}"
            )
        return value


class AtualizarStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Agendamento.Status.choices)


class AgendamentoPorPeriodoSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError(
                "start_date não pode ser posterior a end_date."
            )
        return data
