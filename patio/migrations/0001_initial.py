from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Patio",
            fields=[
                ("id",          models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("nome",        models.CharField(max_length=100, verbose_name="Nome do Pátio")),
                ("localizacao", models.CharField(max_length=255, verbose_name="Localização")),
                ("created_at",  models.DateTimeField(auto_now_add=True)),
                ("updated_at",  models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "patios", "ordering": ["nome"], "verbose_name": "Pátio", "verbose_name_plural": "Pátios"},
        ),
        migrations.CreateModel(
            name="Zona",
            fields=[
                ("id",          models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("patio",       models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="zonas", to="patio.patio", verbose_name="Pátio")),
                ("nome",        models.CharField(max_length=50,  verbose_name="Nome da Zona")),
                ("tipo",        models.CharField(
                    max_length=20,
                    choices=[
                        ("principal",   "Principal"),
                        ("refrigerada", "Refrigerada"),
                        ("expedicao",   "Expedição"),
                        ("recebimento", "Recebimento"),
                        ("reserva",     "Reserva"),
                        ("avariado",    "Avariado"),
                    ],
                    verbose_name="Tipo da Zona",
                )),
                ("capacidade",  models.PositiveIntegerField(verbose_name="Capacidade (pallets)")),
                ("localizacao", models.CharField(blank=True, default="", max_length=255, verbose_name="Localização")),
                ("created_at",  models.DateTimeField(auto_now_add=True)),
                ("updated_at",  models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "zonas", "ordering": ["patio", "nome"], "verbose_name": "Zona", "verbose_name_plural": "Zonas"},
        ),
    ]
