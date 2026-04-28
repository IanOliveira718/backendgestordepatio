from django.urls import path
from . import views

urlpatterns = [
    path("",        views.patio_list_create, name="patio-list-create"),
    path("<int:pk>/", views.patio_detail,   name="patio-detail"),
]
