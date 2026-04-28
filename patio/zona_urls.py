from django.urls import path
from . import views

urlpatterns = [
    path("",          views.zona_list_create, name="zona-list-create"),
    path("<int:pk>/", views.zona_detail,      name="zona-detail"),
]
