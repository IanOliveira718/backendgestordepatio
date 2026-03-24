from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from polls.views_auth import LoginView, RegisterView, MeView

urlpatterns = [
    # Auth — rotas públicas (não exigem token)
    path('api/auth/login/',    LoginView.as_view(),        name='auth-login'),
    path('api/auth/register/', RegisterView.as_view(),     name='auth-register'),
    path('api/auth/refresh/',  TokenRefreshView.as_view(), name='auth-refresh'),
    path('api/auth/me/',       MeView.as_view(),           name='auth-me'),

    # Agendamentos — protegidos por JWT
    path('api/agendamentos/', include('agendamentos.urls')),  # ← agora aponta direto para agendamentos

    path('admin/', admin.site.urls),
]
