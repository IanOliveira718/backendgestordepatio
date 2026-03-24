from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Agendamento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("plate", models.CharField(max_length=20, verbose_name="Placa")),
                ("driver", models.CharField(max_length=150, verbose_name="Motorista")),
                ("type", models.CharField(choices=[("entrada", "Entrada"), ("saida", "Saída")], max_length=10, verbose_name="Tipo")),
                ("zone", models.CharField(max_length=20, verbose_name="Zona")),
                ("date", models.DateField(verbose_name="Data")),
                ("time", models.TimeField(verbose_name="Horário")),
                ("pallets", models.PositiveIntegerField(verbose_name="Quantidade de Pallets")),
                ("status", models.CharField(
                    choices=[("agendado", "Agendado"), ("confirmado", "Confirmado"), ("em_andamento", "Em Andamento"), ("concluido", "Concluído"), ("cancelado", "Cancelado")],
                    default="agendado", max_length=20, verbose_name="Status",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "agendamentos", "ordering": ["date", "time"], "verbose_name": "Agendamento", "verbose_name_plural": "Agendamentos"},
        ),
    ]
