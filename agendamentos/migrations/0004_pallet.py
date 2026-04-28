from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("agendamentos", "0003_tipo_unidade_volume_descricao"),
    ]

    operations = [
        # Cria tabela de pallets controlados
        migrations.CreateModel(
            name="Pallet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False
                    )
                ),

                (
                    "agendamento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pallet_registrados",  # ✅ corrigido aqui
                        to="agendamentos.agendamento",
                        verbose_name="Agendamento",
                    )
                ),

                (
                    "numero_pallet",
                    models.PositiveIntegerField(
                        verbose_name="Número do Pallet"
                    )
                ),

                (
                    "numero_espaco",
                    models.PositiveIntegerField(
                        verbose_name="Número do Espaço"
                    )
                ),

                (
                    "zona_nome",
                    models.CharField(
                        max_length=50,
                        verbose_name="Zona"
                    )
                ),

                (
                    "status",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("pendente", "Pendente"),
                            ("armazenado", "Armazenado"),
                            ("retirado", "Retirado"),
                            ("avariado", "Avariado"),
                        ],
                        default="pendente",
                        verbose_name="Status",
                    )
                ),

                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],

            options={
                "db_table": "pallets",
                "ordering": ["agendamento", "numero_pallet"],
                "verbose_name": "Pallet",
                "verbose_name_plural": "Pallets",
            },
        ),

        migrations.AlterUniqueTogether(
            name="pallet",
            unique_together={("agendamento", "numero_pallet")},
        ),
    ]