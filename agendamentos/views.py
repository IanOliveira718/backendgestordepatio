from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Agendamento, Pallet
from .serializers import (
    AgendamentoSerializer,
    AgendamentoListSerializer,
    AgendamentoDetailSerializer,
    AtualizarStatusSerializer,
    AgendamentoPorPeriodoSerializer,
    PalletSerializer,
    AtualizarStatusPalletSerializer,
)
from agendamentos.permissions import (
    NaoBloqueado,
    IsAdmin,
    IsAdminOuPortariaOuRecebimento,
    IsAdminOuRecebimento,
    IsAdminOuFornecedor,
)


def get_tipo(user):
    try:
        return user.profile.tipo
    except Exception:
        return None


# ── Agendamentos ──────────────────────────────────────────────────────────────

# GET  /api/agendamentos/?date=YYYY-MM-DD
# POST /api/agendamentos/
@api_view(["GET", "POST"])
@permission_classes([NaoBloqueado])
def agendamentos_list_create(request):
    tipo = get_tipo(request.user)

    if request.method == "GET":
        # Admin, portaria e recebimento veem tudo
        # Fornecedor vê apenas os próprios
        if tipo == "fornecedor":
            agendamentos = Agendamento.objects.filter(
                criado_por=request.user
            )
        elif tipo in ("administrador", "portaria", "recebimento"):
            date = request.query_params.get("date")
            if not date:
                return Response(
                    {"error": "Parâmetro 'date' é obrigatório (formato: YYYY-MM-DD)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            agendamentos = Agendamento.objects.filter(date=date)
        else:
            return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)

        return Response(AgendamentoListSerializer(agendamentos, many=True).data)

    # POST — apenas admin e fornecedor
    if tipo not in ("administrador", "fornecedor"):
        return Response(
            {"error": "Sem permissão para criar agendamentos."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AgendamentoSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        agendamento = serializer.save()
        return Response(AgendamentoDetailSerializer(agendamento).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET /api/agendamentos/<id>/
@api_view(["GET"])
@permission_classes([NaoBloqueado])
def agendamento_detail(request, pk):
    tipo = get_tipo(request.user)

    try:
        agendamento = Agendamento.objects.prefetch_related(
            "descricoes_pallets", "descricoes_volumes", "pallet_registrados"
        ).get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response({"error": "Agendamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Fornecedor só vê os próprios
    if tipo == "fornecedor" and agendamento.criado_por != request.user:
        return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)

    return Response(AgendamentoDetailSerializer(agendamento).data)


# PATCH /api/agendamentos/<id>/status/
# Admin, Portaria, Recebimento podem atualizar status
@api_view(["PATCH"])
@permission_classes([NaoBloqueado, IsAdminOuPortariaOuRecebimento])
def atualizar_status(request, pk):
    try:
        agendamento = Agendamento.objects.get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response({"error": "Agendamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if agendamento.status == Agendamento.Status.CANCELADO:
        return Response(
            {"error": "Não é possível alterar o status de um agendamento cancelado."},
            status=status.HTTP_409_CONFLICT,
        )

    serializer = AtualizarStatusSerializer(data=request.data)
    if serializer.is_valid():
        agendamento.status = serializer.validated_data["status"]
        agendamento.save(update_fields=["status", "updated_at"])
        return Response(AgendamentoListSerializer(agendamento).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PATCH /api/agendamentos/<id>/alterar/
# Apenas Admin pode alterar os dados do agendamento
@api_view(["PATCH"])
@permission_classes([NaoBloqueado, IsAdmin])
def alterar(request, pk):
    try:
        agendamento = Agendamento.objects.get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response({"error": "Agendamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if agendamento.status == Agendamento.Status.CANCELADO:
        return Response(
            {"error": "Não é possível alterar um agendamento cancelado."},
            status=status.HTTP_409_CONFLICT,
        )

    serializer = AtualizarStatusSerializer(data=request.data)
    if serializer.is_valid():
        agendamento.status = serializer.validated_data["status"]
        agendamento.save()
        return Response(AgendamentoListSerializer(agendamento).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE /api/agendamentos/<id>/cancelar/
# Apenas Admin pode cancelar
@api_view(["DELETE"])
@permission_classes([NaoBloqueado, IsAdmin])
def cancelar_agendamento(request, pk):
    try:
        agendamento = Agendamento.objects.get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response({"error": "Agendamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if agendamento.status == Agendamento.Status.CONCLUIDO:
        return Response(
            {"error": "Não é possível cancelar um agendamento já concluído."},
            status=status.HTTP_409_CONFLICT,
        )
    if agendamento.status == Agendamento.Status.CANCELADO:
        return Response({"error": "Agendamento já está cancelado."}, status=status.HTTP_409_CONFLICT)

    agendamento.status = Agendamento.Status.CANCELADO
    agendamento.save(update_fields=["status", "updated_at"])
    return Response({"message": f"Agendamento {pk} cancelado com sucesso."})


# GET /api/agendamentos/periodo/
@api_view(["GET"])
@permission_classes([NaoBloqueado, IsAdminOuPortariaOuRecebimento])
def agendamentos_por_periodo(request):
    serializer = AgendamentoPorPeriodoSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    start = serializer.validated_data["start_date"]
    end   = serializer.validated_data["end_date"]
    agendamentos = Agendamento.objects.filter(date__range=(start, end))
    return Response(AgendamentoListSerializer(agendamentos, many=True).data)


# ── Pallets ───────────────────────────────────────────────────────────────────

# GET /api/agendamentos/pallets/
# Admin, Portaria e Recebimento podem ver
@api_view(["GET"])
@permission_classes([NaoBloqueado, IsAdminOuPortariaOuRecebimento])
def pallet_list(request):
    pallets = Pallet.objects.select_related("agendamento").all()

    zona        = request.query_params.get("zona")
    stat        = request.query_params.get("status")
    agendamento = request.query_params.get("agendamento")

    if zona:        pallets = pallets.filter(zona_nome=zona)
    if stat:        pallets = pallets.filter(status=stat)
    if agendamento: pallets = pallets.filter(agendamento_id=agendamento)

    return Response(PalletSerializer(pallets, many=True).data)


# PATCH /api/agendamentos/pallets/<id>/status/
# Apenas Admin e Recebimento podem modificar status de pallets
@api_view(["PATCH"])
@permission_classes([NaoBloqueado, IsAdminOuRecebimento])
def pallet_atualizar_status(request, pk):
    try:
        pallet = Pallet.objects.get(pk=pk)
    except Pallet.DoesNotExist:
        return Response({"error": "Pallet não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    serializer = AtualizarStatusPalletSerializer(data=request.data)
    if serializer.is_valid():
        pallet.status = serializer.validated_data["status"]
        pallet.save(update_fields=["status", "updated_at"])
        return Response(PalletSerializer(pallet).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
