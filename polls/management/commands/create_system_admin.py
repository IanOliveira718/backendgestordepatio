"""
Comando para criar o administrador do sistema pré-configurado.
Execute uma vez após aplicar as migrations:

    python manage.py create_system_admin

As credenciais podem ser definidas via variáveis de ambiente:
    SYSTEM_ADMIN_USERNAME  (padrão: admin)
    SYSTEM_ADMIN_PASSWORD  (padrão: Admin@2024!)
    SYSTEM_ADMIN_EMAIL     (padrão: admin@sistema.local)
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from polls.models import UserProfile


class Command(BaseCommand):
    help = "Cria o administrador do sistema pré-configurado (imutável por outros admins)."

    def handle(self, *args, **options):
        username = os.environ.get("SYSTEM_ADMIN_USERNAME", "admin")
        password = os.environ.get("SYSTEM_ADMIN_PASSWORD", "Admin@2024!")
        email    = os.environ.get("SYSTEM_ADMIN_EMAIL",    "admin@sistema.local")

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Usuário '{username}' já existe. Nenhuma ação realizada."))
            return

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name="Administrador",
            last_name="do Sistema",
            is_staff=True,
        )

        UserProfile.objects.create(
            user=user,
            tipo="administrador",
            bloqueado=False,
            is_system_admin=True,
        )

        self.stdout.write(self.style.SUCCESS(
            f"Admin do sistema criado com sucesso!\n"
            f"  Usuário: {username}\n"
            f"  Senha:   {password}\n"
            f"  ⚠️  Troque a senha no primeiro acesso."
        ))
