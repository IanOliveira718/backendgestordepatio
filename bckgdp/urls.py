from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from polls.views_auth import LoginView, RegisterView, MeView
from agendamentos.views_configuracao import configuracao_view

urlpatterns = [
    # Auth — rotas públicas (não exigem token)
    path('api/auth/login/',    LoginView.as_view(),        name='auth-login'),
    path('api/auth/register/', RegisterView.as_view(),     name='auth-register'),
    path('api/auth/refresh/',  TokenRefreshView.as_view(), name='auth-refresh'),
    path('api/auth/me/',       MeView.as_view(),           name='auth-me'),
    path('api/patios/', include('patio.urls')),
    path('api/zonas/',  include('patio.zona_urls')),
    path('api/config/', configuracao_view, name='configuracao'),
    
    # Agendamentos — protegidos por JWT
    path('api/agendamentos/', include('agendamentos.urls')),  # ← agora aponta direto para agendamentos
    path('api/users/', include('polls.urls_users')),
    path('admin/', admin.site.urls),
]