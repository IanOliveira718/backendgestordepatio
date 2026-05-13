from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from polls.models import UserProfile
from .serializers_users import (
    UserSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
    ChangePasswordSerializer,
)


def _is_admin(user):
    try:
        return user.profile.tipo == "administrador" and not user.profile.bloqueado
    except UserProfile.DoesNotExist:
        return False


def _is_system_admin(user):
    try:
        return user.profile.is_system_admin
    except UserProfile.DoesNotExist:
        return False


# GET  /api/users/          — lista todos os usuários (admin only)
# POST /api/users/          — cria novo usuário (admin only)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_list_create(request):
    if not _is_admin(request.user):
        return Response({"error": "Acesso restrito a administradores."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        users = User.objects.select_related("profile").all().order_by("username")
        return Response(UserSerializer(users, many=True).data)

    serializer = CreateUserSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET   /api/users/<id>/    — detalhe
# PATCH /api/users/<id>/    — atualiza informações
# DELETE /api/users/<id>/   — exclui usuário
@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    if not _is_admin(request.user):
        return Response({"error": "Acesso restrito a administradores."}, status=status.HTTP_403_FORBIDDEN)

    try:
        target = User.objects.select_related("profile").get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(UserSerializer(target).data)

    # Proteção: admin do sistema não pode ser alterado nem excluído por ninguém
    if hasattr(target, "profile") and target.profile.is_system_admin:
        return Response(
            {"error": "O administrador do sistema não pode ser alterado ou excluído."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "PATCH":
        serializer = UpdateUserSerializer(
            data=request.data,
            context={"request": request, "target_user": target},
        )
        if serializer.is_valid():
            data = serializer.validated_data
            # Atualiza campos do User
            for field in ["email", "first_name", "last_name"]:
                if field in data:
                    setattr(target, field, data[field])
            target.save()
            # Atualiza tipo no perfil
            if "tipo" in data:
                target.profile.tipo = data["tipo"]
                target.profile.save(update_fields=["tipo", "updated_at"])
            return Response(UserSerializer(target).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    # Admin não pode excluir a si mesmo
    if target.pk == request.user.pk:
        return Response(
            {"error": "Você não pode excluir sua própria conta."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    target.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# PATCH /api/users/<id>/senha/   — redefinir senha (admin only)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def user_change_password(request, pk):
    if not _is_admin(request.user):
        return Response({"error": "Acesso restrito a administradores."}, status=status.HTTP_403_FORBIDDEN)

    try:
        target = User.objects.select_related("profile").get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if hasattr(target, "profile") and target.profile.is_system_admin:
        return Response(
            {"error": "A senha do administrador do sistema não pode ser redefinida por outros admins."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        target.set_password(serializer.validated_data["password"])
        target.save()
        return Response({"message": "Senha redefinida com sucesso."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PATCH /api/users/<id>/acesso/   — bloquear ou desbloquear (admin only)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def user_toggle_acesso(request, pk):
    if not _is_admin(request.user):
        return Response({"error": "Acesso restrito a administradores."}, status=status.HTTP_403_FORBIDDEN)

    try:
        target = User.objects.select_related("profile").get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if hasattr(target, "profile") and target.profile.is_system_admin:
        return Response(
            {"error": "O administrador do sistema não pode ter o acesso bloqueado."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if target.pk == request.user.pk:
        return Response(
            {"error": "Você não pode bloquear a si mesmo."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    bloqueado = request.data.get("bloqueado")
    if bloqueado is None:
        return Response({"error": "Campo 'bloqueado' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    target.profile.bloqueado = bool(bloqueado)
    target.profile.save(update_fields=["bloqueado", "updated_at"])
    return Response(UserSerializer(target).data)
