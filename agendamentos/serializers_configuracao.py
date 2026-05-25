from rest_framework import serializers
from .models_configuracao import Configuracao


class ConfiguracaoSerializer(serializers.ModelSerializer):
    janela_total_horas = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Configuracao
        fields = ["janela_dias", "janela_horas", "janela_total_horas", "updated_at"]
        read_only_fields = ["updated_at"]

    def validate_janela_horas(self, value):
        if value > 23:
            raise serializers.ValidationError(
                "Janela de horas deve ser entre 0 e 23. Use o campo 'janela_dias' para dias completos."
            )
        return value

    def validate(self, data):
        dias  = data.get("janela_dias",  self.instance.janela_dias  if self.instance else 0)
        horas = data.get("janela_horas", self.instance.janela_horas if self.instance else 24)
        if dias == 0 and horas == 0:
            raise serializers.ValidationError("A janela de tempo não pode ser zero.")
        return data
