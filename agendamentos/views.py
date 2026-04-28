from rest_framework import status
from rest_framework.decorators import api_view
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


# ── Agendamentos ──────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
def agendamentos_list_create(request):
    if request.method == "GET":
        date = request.query_params.get("date")
        if not date:
            return Response(
                {"error": "Parâmetro 'date' é obrigatório (formato: YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        agendamentos = Agendamento.objects.filter(date=date)
        return Response(AgendamentoListSerializer(agendamentos, many=True).data)

    serializer = AgendamentoSerializer(data=request.data)
    if serializer.is_valid():
        agendamento = serializer.save()
        return Response(AgendamentoDetailSerializer(agendamento).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def agendamento_detail(request, pk):
    try:
        agendamento = Agendamento.objects.prefetch_related(
            "descricoes_pallets", "descricoes_volumes", "pallets"
        ).get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response({"error": "Agendamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    return Response(AgendamentoDetailSerializer(agendamento).data)


@api_view(["PATCH"])
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


@api_view(["PATCH"])
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


@api_view(["DELETE"])
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


@api_view(["GET"])
def agendamentos_por_periodo(request):
    serializer = AgendamentoPorPeriodoSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    start = serializer.validated_data["start_date"]
    end   = serializer.validated_data["end_date"]
    agendamentos = Agendamento.objects.filter(date__range=(start, end))
    return Response(AgendamentoListSerializer(agendamentos, many=True).data)


# ── Pallets ───────────────────────────────────────────────────────────────────

# GET /api/pallets/
# Query params opcionais: ?zona=<nome> &status=<status> &agendamento=<id>
@api_view(["GET"])
def pallet_list(request):
    pallets = Pallet.objects.select_related("agendamento").all()

    zona        = request.query_params.get("zona")
    stat        = request.query_params.get("status")
    agendamento = request.query_params.get("agendamento")

    if zona:
        pallets = pallets.filter(zona_nome=zona)
    if stat:
        pallets = pallets.filter(status=stat)
    if agendamento:
        pallets = pallets.filter(agendamento_id=agendamento)

    return Response(PalletSerializer(pallets, many=True).data)


# PATCH /api/pallets/<id>/status/
@api_view(["PATCH"])
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
