from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from agendamentos.permissions import NaoBloqueado, IsAdmin
from .models import Fornecedor
from .serializers_fornecedor import FornecedorSerializer, FornecedorListSerializer, FornecedorPublicoSerializer


def _paginar(qs, request, serializer_class):
    """Paginação simples por query params."""
    page     = max(int(request.query_params.get("page", 1)), 1)
    per_page = max(int(request.query_params.get("per_page", 10)), 1)
    total    = qs.count()
    start    = (page - 1) * per_page
    end      = start + per_page

    return {
        "count":    total,
        "page":     page,
        "per_page": per_page,
        "pages":    (total + per_page - 1) // per_page,
        "results":  serializer_class(qs[start:end], many=True).data,
    }


# GET  /api/fornecedores/        — admin: todos; público: apenas ativos (para cadastro)
# POST /api/fornecedores/        — apenas admin
@api_view(["GET", "POST"])
def fornecedor_list_create(request):
    if request.method == "GET":
        is_admin = (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.tipo == "administrador"
            and not request.user.profile.bloqueado
        )

        qs = Fornecedor.objects.all() if is_admin else Fornecedor.objects.filter(ativo=True)

        # Busca
        q = request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(nome_fantasia__icontains=q) | qs.filter(cnpj__icontains=q.replace(".", "").replace("/", "").replace("-", ""))

        # Filtro ativo (só admin)
        ativo = request.query_params.get("ativo")
        if is_admin and ativo in ("true", "false"):
            qs = qs.filter(ativo=ativo == "true")

        serializer = FornecedorListSerializer if is_admin else FornecedorPublicoSerializer
        return Response(_paginar(qs, request, serializer))

    # POST — apenas admin
    if not request.user.is_authenticated:
        return Response({"error": "Autenticação necessária."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if request.user.profile.tipo != "administrador" or request.user.profile.bloqueado:
            return Response({"error": "Acesso restrito a administradores."}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)

    serializer = FornecedorSerializer(data=request.data)
    if serializer.is_valid():
        fornecedor = serializer.save()
        return Response(FornecedorSerializer(fornecedor).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET    /api/fornecedores/<id>/
# PATCH  /api/fornecedores/<id>/
# DELETE /api/fornecedores/<id>/
@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([NaoBloqueado, IsAdmin])
def fornecedor_detail(request, pk):
    try:
        fornecedor = Fornecedor.objects.get(pk=pk)
    except Fornecedor.DoesNotExist:
        return Response({"error": "Fornecedor não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(FornecedorSerializer(fornecedor).data)

    if request.method == "PATCH":
        serializer = FornecedorSerializer(fornecedor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(FornecedorSerializer(fornecedor).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE — bloqueia se tiver usuários vinculados
    if fornecedor.usuarios.exists():
        return Response(
            {"error": "Este fornecedor possui usuários vinculados. Desative-o em vez de excluir."},
            status=status.HTTP_409_CONFLICT,
        )
    fornecedor.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# PATCH /api/fornecedores/<id>/status/  — ativar ou desativar
@api_view(["PATCH"])
@permission_classes([NaoBloqueado, IsAdmin])
def fornecedor_toggle_status(request, pk):
    try:
        fornecedor = Fornecedor.objects.get(pk=pk)
    except Fornecedor.DoesNotExist:
        return Response({"error": "Fornecedor não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    ativo = request.data.get("ativo")
    if ativo is None:
        return Response({"error": "Campo 'ativo' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    fornecedor.ativo = bool(ativo)
    fornecedor.save(update_fields=["ativo", "updated_at"])
    return Response(FornecedorSerializer(fornecedor).data)