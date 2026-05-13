from django.urls import path
from . import views_users

urlpatterns = [
    path("",                       views_users.user_list_create,    name="user-list-create"),
    path("<int:pk>/",              views_users.user_detail,         name="user-detail"),
    path("<int:pk>/senha/",        views_users.user_change_password, name="user-change-password"),
    path("<int:pk>/acesso/",       views_users.user_toggle_acesso,  name="user-toggle-acesso"),
]
