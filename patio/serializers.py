from rest_framework import serializers
from .models import Patio, Zona


class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Zona
        fields = [
            "id", "patio", "nome", "tipo",
            "capacidade", "localizacao",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ZonaInlineSerializer(serializers.ModelSerializer):
    """Zonas embutidas dentro do pátio — sem o campo patio (redundante)."""
    class Meta:
        model  = Zona
        fields = ["id", "nome", "tipo", "capacidade", "localizacao"]
        read_only_fields = ["id"]


class PatioSerializer(serializers.ModelSerializer):
    zonas        = ZonaInlineSerializer(many=True, read_only=True)
    total_zonas  = serializers.SerializerMethodField()
    capacidade_total = serializers.SerializerMethodField()

    class Meta:
        model  = Patio
        fields = [
            "id", "nome", "localizacao",
            "total_zonas", "capacidade_total",
            "zonas", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_total_zonas(self, obj):
        return obj.zonas.count()

    def get_capacidade_total(self, obj):
        return sum(z.capacidade for z in obj.zonas.all())


class PatioListSerializer(serializers.ModelSerializer):
    """Versão leve para listagem — sem zonas aninhadas."""
    total_zonas      = serializers.SerializerMethodField()
    capacidade_total = serializers.SerializerMethodField()

    class Meta:
        model  = Patio
        fields = [
            "id", "nome", "localizacao",
            "total_zonas", "capacidade_total",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_total_zonas(self, obj):
        return obj.zonas.count()

    def get_capacidade_total(self, obj):
        return sum(z.capacidade for z in obj.zonas.all())
