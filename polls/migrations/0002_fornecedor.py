from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ("polls", "0001_userprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="Fornecedor",
            fields=[
                ("id",            models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("cnpj",          models.CharField(max_length=14, unique=True, verbose_name="CNPJ")),
                ("razao_social",  models.CharField(max_length=200, verbose_name="Razão Social")),
                ("nome_fantasia", models.CharField(max_length=150, verbose_name="Nome Fantasia")),
                ("ativo",         models.BooleanField(default=True, verbose_name="Ativo")),
                ("created_at",    models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")),
                ("updated_at",    models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "fornecedores",
                "ordering": ["nome_fantasia"],
                "verbose_name": "Fornecedor",
                "verbose_name_plural": "Fornecedores",
            },
        ),
    ]