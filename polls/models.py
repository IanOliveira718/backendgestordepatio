from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Estende o User do Django com tipo e status de acesso."""

    class Tipo(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        PORTARIA      = "portaria",      "Portaria"
        RECEBIMENTO   = "recebimento",   "Recebimento"
        FORNECEDOR    = "fornecedor",    "Fornecedor"

    # Hierarquia numérica — admin só pode criar tipos de nível inferior
    HIERARQUIA = {
        "administrador": 4,
        "portaria":      3,
        "recebimento":   2,
        "fornecedor":    1,
    }

    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    tipo      = models.CharField(max_length=20, choices=Tipo.choices, verbose_name="Tipo")
    bloqueado = models.BooleanField(default=False, verbose_name="Acesso Bloqueado")

    # Flag que marca o superusuário pré-configurado — ninguém pode alterar ou excluir
    is_system_admin = models.BooleanField(default=False, verbose_name="Admin do Sistema")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = "user_profiles"
        verbose_name        = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"{self.user.username} ({self.tipo})"