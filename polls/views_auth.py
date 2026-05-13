from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers_auth import RegisterSerializer, UserSerializer
from .models import UserProfile


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


def _user_response(user):
    """Monta resposta completa com tokens + dados do usuário incluindo tipo."""
    data = UserSerializer(user).data
    # Adiciona tipo e status do perfil se existir
    try:
        data["tipo"]            = user.profile.tipo
        data["bloqueado"]       = user.profile.bloqueado
        data["is_system_admin"] = user.profile.is_system_admin
    except UserProfile.DoesNotExist:
        data["tipo"]            = None
        data["bloqueado"]       = False
        data["is_system_admin"] = False
    return data


# POST /api/auth/login/
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Informe username e password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"error": "Credenciais inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Verifica se o acesso está bloqueado
        try:
            if user.profile.bloqueado:
                return Response(
                    {"error": "Acesso bloqueado. Entre em contato com o administrador."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except UserProfile.DoesNotExist:
            pass  # Usuário sem perfil ainda — permite login

        tokens = _tokens_for_user(user)
        return Response({**tokens, "user": _user_response(user)})


# POST /api/auth/register/
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user   = serializer.save()
            tokens = _tokens_for_user(user)
            return Response(
                {**tokens, "user": _user_response(user)},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET /api/auth/me/
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_user_response(request.user))
