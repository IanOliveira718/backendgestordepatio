from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from agendamentos.permissions import NaoBloqueado, IsAdmin
from .models_configuracao import Configuracao
from .serializers_configuracao import ConfiguracaoSerializer


# GET  /api/config/        — qualquer usuário autenticado pode ver
# PATCH /api/config/       — apenas admin pode alterar
@api_view(["GET", "PATCH"])
@permission_classes([NaoBloqueado])
def configuracao_view(request):
    config = Configuracao.get()

    if request.method == "GET":
        return Response(ConfiguracaoSerializer(config).data)

    # PATCH — só admin
    if not hasattr(request.user, "profile") or request.user.profile.tipo != "administrador":
        return Response(
            {"error": "Acesso restrito a administradores."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ConfiguracaoSerializer(config, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
