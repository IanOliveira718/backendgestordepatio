from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("polls",         "0001_userprofile"),   # última migration do app polls
        ("polls",  "0002_fornecedor"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="pendente",
            field=models.BooleanField(default=False, verbose_name="Aprovação Pendente"),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="fornecedor",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="usuarios",
                to="polls.fornecedor",
                verbose_name="Fornecedor",
            ),
        ),
    ]
