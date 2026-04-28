from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Patio, Zona
from .serializers import (
    PatioSerializer, PatioListSerializer,
    ZonaSerializer,
)


# ── Pátios ────────────────────────────────────────────────────────────────────

# GET  /api/patios/       — lista todos
# POST /api/patios/       — cria novo
@api_view(["GET", "POST"])
def patio_list_create(request):
    if request.method == "GET":
        patios = Patio.objects.prefetch_related("zonas").all()
        return Response(PatioListSerializer(patios, many=True).data)

    serializer = PatioSerializer(data=request.data)
    if serializer.is_valid():
        patio = serializer.save()
        return Response(PatioSerializer(patio).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET    /api/patios/<id>/   — detalhe com zonas
# PATCH  /api/patios/<id>/   — atualiza
# DELETE /api/patios/<id>/   — remove
@api_view(["GET", "PATCH", "DELETE"])
def patio_detail(request, pk):
    try:
        patio = Patio.objects.prefetch_related("zonas").get(pk=pk)
    except Patio.DoesNotExist:
        return Response({"error": "Pátio não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(PatioSerializer(patio).data)

    if request.method == "PATCH":
        serializer = PatioSerializer(patio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(PatioSerializer(patio).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    if patio.zonas.exists():
        return Response(
            {"error": "Não é possível excluir um pátio que possui zonas. Remova as zonas primeiro."},
            status=status.HTTP_409_CONFLICT,
        )
    patio.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Zonas ─────────────────────────────────────────────────────────────────────

# GET  /api/zonas/         — lista todas (opcionalmente filtrada por ?patio=<id>)
# POST /api/zonas/         — cria nova
@api_view(["GET", "POST"])
def zona_list_create(request):
    if request.method == "GET":
        zonas = Zona.objects.select_related("patio").all()
        patio_id = request.query_params.get("patio")
        if patio_id:
            zonas = zonas.filter(patio_id=patio_id)
        return Response(ZonaSerializer(zonas, many=True).data)

    serializer = ZonaSerializer(data=request.data)
    if serializer.is_valid():
        zona = serializer.save()
        return Response(ZonaSerializer(zona).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET    /api/zonas/<id>/  — detalhe
# PATCH  /api/zonas/<id>/  — atualiza
# DELETE /api/zonas/<id>/  — remove
@api_view(["GET", "PATCH", "DELETE"])
def zona_detail(request, pk):
    try:
        zona = Zona.objects.select_related("patio").get(pk=pk)
    except Zona.DoesNotExist:
        return Response({"error": "Zona não encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(ZonaSerializer(zona).data)

    if request.method == "PATCH":
        serializer = ZonaSerializer(zona, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ZonaSerializer(zona).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    zona.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
