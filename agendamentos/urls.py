from django.urls import path
from . import views

urlpatterns = [
     path("periodo/", views.agendamentos_por_periodo, name="agendamentos-periodo"),
    path("", views.agendamentos_list_create, name="agendamentos-list-create"),
    path("<int:pk>/status/", views.atualizar_status, name="agendamentos-status"),
    #path("<int:pk>/alterar/", views.alterar, name="agendamentos-alterar"),
    path("<int:pk>/cancelar/", views.cancelar_agendamento, name="agendamentos-cancelar"),
]
