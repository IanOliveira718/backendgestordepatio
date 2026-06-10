import re
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from polls.models import UserProfile
from polls.models import Fornecedor


def _only_digits(v: str) -> str:
    return re.sub(r"\D", "", v)

class RegisterSerializer(serializers.Serializer):
    """
    Auto-cadastro público.
    Sempre cria como fornecedor, bloqueado=True e pendente=True.
    Valida CNPJ contra a tabela de fornecedores cadastrados pelo admin.
    """
    username   = serializers.CharField(max_length=150)
    email      = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name  = serializers.CharField(max_length=150, required=False, default="")
    password   = serializers.CharField(write_only=True, validators=[validate_password])
    password2  = serializers.CharField(write_only=True, label="Confirmar senha")
    cnpj       = serializers.CharField(max_length=18)
 
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value
 
    def validate_cnpj(self, value):
        digits = _only_digits(value)
        if len(digits) != 14:
            raise serializers.ValidationError("CNPJ deve ter 14 dígitos.")
 
        #if not FORNECEDOR_APP:
        #    raise serializers.ValidationError(
        #        "Módulo de fornecedores não disponível. Contate o administrador."
        #    )
 
        try:
            fornecedor = Fornecedor.objects.get(cnpj=digits)
        except Fornecedor.DoesNotExist:
            raise serializers.ValidationError(
                "CNPJ não possui vínculo com nenhuma empresa cadastrada no sistema. "
                "Entre em contato com o administrador."
            )
 
        if not fornecedor.ativo:
            raise serializers.ValidationError(
                "A empresa vinculada a este CNPJ está inativa. "
                "Entre em contato com o administrador."
            )
 
        return digits
 
    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return data
 
    def create(self, validated_data):
        validated_data.pop("password2")
        cnpj = validated_data.pop("cnpj")
        fornecedor = Fornecedor.objects.get(cnpj=cnpj)
 
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ""),
        )
 
        UserProfile.objects.create(
            user=user,
            tipo="fornecedor",
            bloqueado=True,
            pendente=True,
            fornecedor=fornecedor,
        )
 
        return user
 
 
class UserSerializer(serializers.ModelSerializer):
    tipo            = serializers.CharField(source="profile.tipo",               read_only=True)
    bloqueado       = serializers.BooleanField(source="profile.bloqueado",       read_only=True)
    pendente        = serializers.BooleanField(source="profile.pendente",        read_only=True)
    is_system_admin = serializers.BooleanField(source="profile.is_system_admin", read_only=True)
 
    class Meta:
        model  = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "tipo", "bloqueado", "pendente", "is_system_admin",
        ]