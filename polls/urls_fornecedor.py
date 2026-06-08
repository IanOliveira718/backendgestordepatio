from django.urls import path
from . import views_fornecedor

urlpatterns = [
    path("",              views_fornecedor.fornecedor_list_create,   name="fornecedor-list-create"),
    path("<int:pk>/",     views_fornecedor.fornecedor_detail,        name="fornecedor-detail"),
    path("<int:pk>/status/", views_fornecedor.fornecedor_toggle_status, name="fornecedor-status"),
]