import re
from rest_framework import serializers
from .models import Fornecedor


def _only_digits(v: str) -> str:
    return re.sub(r"\D", "", v)


def _validate_cnpj_digits(digits: str) -> bool:
    """Validação do dígito verificador do CNPJ."""
    if len(digits) != 14 or len(set(digits)) == 1:
        return False

    def calc(digits, weights):
        total = sum(int(d) * w for d, w in zip(digits, weights))
        rest  = total % 11
        return 0 if rest < 2 else 11 - rest

    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    return (
        calc(digits[:12], w1) == int(digits[12]) and
        calc(digits[:13], w2) == int(digits[13])
    )


class FornecedorSerializer(serializers.ModelSerializer):
    cnpj_formatado = serializers.CharField(read_only=True)

    class Meta:
        model  = Fornecedor
        fields = [
            "id", "cnpj", "cnpj_formatado", "razao_social",
            "nome_fantasia", "ativo", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "cnpj_formatado", "created_at", "updated_at"]

    def validate_cnpj(self, value):
        digits = _only_digits(value)
        if not _validate_cnpj_digits(digits):
            raise serializers.ValidationError("CNPJ inválido.")
        qs = Fornecedor.objects.filter(cnpj=digits)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Já existe um fornecedor com este CNPJ.")
        return digits


class FornecedorListSerializer(serializers.ModelSerializer):
    """Versão leve para listagem."""
    cnpj_formatado = serializers.CharField(read_only=True)

    class Meta:
        model  = Fornecedor
        fields = ["id", "cnpj", "cnpj_formatado", "nome_fantasia", "razao_social", "ativo", "created_at"]


class FornecedorPublicoSerializer(serializers.ModelSerializer):
    """Exposição mínima para o formulário de cadastro de usuário."""
    cnpj_formatado = serializers.CharField(read_only=True)

    class Meta:
        model  = Fornecedor
        fields = ["id", "cnpj", "cnpj_formatado", "nome_fantasia"]