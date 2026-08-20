from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("agendamentos", "0006_configuracao")
    ]

    operations = [
        migrations.AddField(
            model_name="agendamento",
            name="urgente",
            field=models.PositiveIntegerField(verbose_name="Urgente", default=0),
    ),
    ]
