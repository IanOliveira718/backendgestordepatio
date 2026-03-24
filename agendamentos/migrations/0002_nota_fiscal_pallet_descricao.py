from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("agendamentos", "0001_initial"),
    ]

    operations = [
        # Adiciona nota_fiscal à tabela de agendamentos
        migrations.AddField(
            model_name="agendamento",
            name="nota_fiscal",
            field=models.CharField(default="", max_length=60, verbose_name="Nota Fiscal"),
            preserve_default=False,
        ),
        # Cria a tabela de descrições de pallets
        migrations.CreateModel(
            name="PalletDescricao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("agendamento", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="descricoes_pallets",
                    to="agendamentos.agendamento",
                    verbose_name="Agendamento",
                )),
                ("ordem",     models.PositiveSmallIntegerField(verbose_name="Ordem do Pallet")),
                ("descricao", models.CharField(max_length=255, verbose_name="Descrição")),
            ],
            options={
                "db_table": "pallet_descricoes",
                "ordering": ["agendamento", "ordem"],
                "verbose_name": "Descrição de Pallet",
                "verbose_name_plural": "Descrições de Pallets",
            },
        ),
        migrations.AlterUniqueTogether(
            name="palletdescricao",
            unique_together={("agendamento", "ordem")},
        ),
    ]
