from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from polls.models import UserProfile


HIERARQUIA = UserProfile.HIERARQUIA


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = ["tipo", "bloqueado", "is_system_admin"]
        read_only_fields = ["is_system_admin"]


class UserSerializer(serializers.ModelSerializer):
    """Retorna dados do usuário + perfil para o endpoint /me/ e listagem."""
    tipo            = serializers.CharField(source="profile.tipo",            read_only=True)
    bloqueado       = serializers.BooleanField(source="profile.bloqueado",    read_only=True)
    is_system_admin = serializers.BooleanField(source="profile.is_system_admin", read_only=True)

    class Meta:
        model  = User
        fields = [
            "id", "username", "email",
            "first_name", "last_name",
            "tipo", "bloqueado", "is_system_admin",
            "date_joined",
        ]


class CreateUserSerializer(serializers.Serializer):
    """Admin cria um novo usuário."""
    username   = serializers.CharField(max_length=150)
    email      = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name  = serializers.CharField(max_length=150, required=False, default="")
    password   = serializers.CharField(write_only=True, validators=[validate_password])
    tipo       = serializers.ChoiceField(choices=UserProfile.Tipo.choices)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def validate(self, data):
        # Admin só pode criar usuários de nível inferior ao seu
        request_user = self.context["request"].user
        try:
            admin_tipo = request_user.profile.tipo
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Perfil do solicitante não encontrado.")

        nivel_admin = HIERARQUIA.get(admin_tipo, 0)
        nivel_novo  = HIERARQUIA.get(data["tipo"], 0)

        if nivel_novo >= nivel_admin:
            raise serializers.ValidationError({
                "tipo": f"Você não pode criar usuários do tipo '{data['tipo']}'. "
                        f"Apenas tipos de nível inferior ao seu ({admin_tipo}) são permitidos."
            })
        return data

    def create(self, validated_data):
        tipo = validated_data.pop("tipo")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ""),
        )
        UserProfile.objects.create(user=user, tipo=tipo)
        return user


class UpdateUserSerializer(serializers.Serializer):
    """Admin atualiza informações de outro usuário."""
    email      = serializers.EmailField(required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name  = serializers.CharField(max_length=150, required=False)
    tipo       = serializers.ChoiceField(choices=UserProfile.Tipo.choices, required=False)

    def validate(self, data):
        request_user = self.context["request"].user
        target_user  = self.context["target_user"]

        # Não pode alterar o admin do sistema
        if hasattr(target_user, "profile") and target_user.profile.is_system_admin:
            raise serializers.ValidationError(
                "O administrador do sistema não pode ser alterado."
            )

        # Valida hierarquia se tipo for alterado
        if "tipo" in data:
            try:
                admin_tipo = request_user.profile.tipo
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError("Perfil do solicitante não encontrado.")

            nivel_admin = HIERARQUIA.get(admin_tipo, 0)
            nivel_novo  = HIERARQUIA.get(data["tipo"], 0)

            if nivel_novo >= nivel_admin:
                raise serializers.ValidationError({
                    "tipo": f"Você não pode definir o tipo '{data['tipo']}' para este usuário."
                })
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Admin redefine senha de outro usuário."""
    password = serializers.CharField(write_only=True, validators=[validate_password])


# Serializer de login — reutiliza o existente no views_auth.py
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
