from django.db import migrations, models


class Migration(migrations.Migration):

    # Ajuste para a última migration do app onde ficará esse model
    dependencies = [
        ("agendamentos", "0005_agendamento_criado_por"),
    ]

    operations = [
        migrations.CreateModel(
            name="Configuracao",
            fields=[
                ("id",           models.AutoField(primary_key=True, serialize=False)),
                ("janela_dias",  models.PositiveIntegerField(default=0,  verbose_name="Janela — dias")),
                ("janela_horas", models.PositiveIntegerField(default=24, verbose_name="Janela — horas")),
                ("updated_at",   models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "configuracoes", "verbose_name": "Configuração do Sistema"},
        ),
        # Garante que o registro singleton já existe após a migration
        migrations.RunSQL(
            sql="INSERT INTO configuracoes (id, janela_dias, janela_horas, updated_at) "
                "VALUES (1, 0, 24, CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING;",
            reverse_sql="DELETE FROM configuracoes WHERE id = 1;",
        ),
    ]
