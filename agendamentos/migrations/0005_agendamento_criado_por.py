from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("agendamentos", "0004_pallet"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="agendamento",
            name="criado_por",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="agendamentos",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Criado por",
            ),
        ),
    ]
