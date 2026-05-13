from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id",              models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("user",            models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="profile",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("tipo",            models.CharField(
                    max_length=20,
                    choices=[
                        ("administrador", "Administrador"),
                        ("portaria",      "Portaria"),
                        ("recebimento",   "Recebimento"),
                        ("fornecedor",    "Fornecedor"),
                    ],
                    verbose_name="Tipo",
                )),
                ("bloqueado",       models.BooleanField(default=False, verbose_name="Acesso Bloqueado")),
                ("is_system_admin", models.BooleanField(default=False, verbose_name="Admin do Sistema")),
                ("created_at",      models.DateTimeField(auto_now_add=True)),
                ("updated_at",      models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table":             "user_profiles",
                "verbose_name":         "Perfil de Usuário",
                "verbose_name_plural":  "Perfis de Usuários",
            },
        ),
    ]
