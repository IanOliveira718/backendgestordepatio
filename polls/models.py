from django.db import models
from django.contrib.auth.models import User
import re
from django.db import models

def _only_digits(value: str) -> str:
    return re.sub(r"\D", "", value)

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

class Fornecedor(models.Model):
    cnpj          = models.CharField(max_length=14, unique=True, verbose_name="CNPJ")
    razao_social  = models.CharField(max_length=200, verbose_name="Razão Social")
    nome_fantasia = models.CharField(max_length=150, verbose_name="Nome Fantasia")
    ativo         = models.BooleanField(default=True, verbose_name="Ativo")
    created_at    = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    updated_at    = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table            = "fornecedores"
        ordering            = ["nome_fantasia"]
        verbose_name        = "Fornecedor"
        verbose_name_plural = "Fornecedores"
 
    def save(self, *args, **kwargs):
        self.cnpj = _only_digits(self.cnpj)
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.nome_fantasia} ({self.cnpj_formatado})"
 
    @property
    def cnpj_formatado(self) -> str:
        c = self.cnpj.zfill(14)
        return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"
 