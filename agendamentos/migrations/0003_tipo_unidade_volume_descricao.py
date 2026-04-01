from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("agendamentos", "0002_nota_fiscal_pallet_descricao"),
    ]

    operations = [
        # Adiciona tipo_unidade em Agendamento
        migrations.AddField(
            model_name="agendamento",
            name="tipo_unidade",
            field=models.CharField(
                choices=[("pallet", "Pallet"), ("volume", "Volume")],
                default="pallet",
                max_length=10,
                verbose_name="Tipo de Unidade",
            ),
        ),
        # Cria tabela de descrições de volume
        migrations.CreateModel(
            name="VolumeDescricao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("agendamento", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="descricoes_volumes",
                    to="agendamentos.agendamento",
                    verbose_name="Agendamento",
                )),
                ("ordem",       models.PositiveSmallIntegerField(verbose_name="Ordem do Volume")),
                ("descricao",   models.CharField(max_length=255, verbose_name="Descrição")),
                ("altura",      models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Altura (cm)")),
                ("largura",     models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Largura (cm)")),
                ("comprimento", models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Comprimento (cm)")),
            ],
            options={
                "db_table": "volume_descricoes",
                "ordering": ["agendamento", "ordem"],
                "verbose_name": "Descrição de Volume",
                "verbose_name_plural": "Descrições de Volumes",
            },
        ),
        migrations.AlterUniqueTogether(
            name="volumedescricao",
            unique_together={("agendamento", "ordem")},
        ),
    ]
