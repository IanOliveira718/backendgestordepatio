from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Agendamento
from .serializers import (
    AgendamentoSerializer,
    AtualizarStatusSerializer,
    AgendamentoPorPeriodoSerializer,
)

# Listar do dia / 2. Criar
# GET  /api/agendamentos/?date=YYYY-MM-DD
# POST /api/agendamentos/
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
        return Response(AgendamentoSerializer(agendamentos, many=True).data)

    serializer = AgendamentoSerializer(data=request.data)
    if serializer.is_valid():
        agendamento = serializer.save()
        return Response(AgendamentoSerializer(agendamento).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Atualizar status
# PATCH /api/agendamentos/<id>/status/
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
        return Response(AgendamentoSerializer(agendamento).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Cancelar
# DELETE /api/agendamentos/<id>/cancelar/
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


# 5. Listar por período
# GET /api/agendamentos/periodo/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
@api_view(["GET"])
def agendamentos_por_periodo(request):
    serializer = AgendamentoPorPeriodoSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    start = serializer.validated_data["start_date"]
    end = serializer.validated_data["end_date"]
    agendamentos = Agendamento.objects.filter(date__range=(start, end))
    return Response(AgendamentoSerializer(agendamentos, many=True).data)
