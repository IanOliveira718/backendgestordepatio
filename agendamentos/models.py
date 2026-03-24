from django.db import models


class Agendamento(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SAIDA = "saida", "Saída"

    class Status(models.TextChoices):
        AGENDADO = "agendado", "Agendado"
        CONFIRMADO = "confirmado", "Confirmado"
        EM_ANDAMENTO = "em_andamento", "Em Andamento"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    plate = models.CharField(max_length=20, verbose_name="Placa")
    driver = models.CharField(max_length=150, verbose_name="Motorista")
    type = models.CharField(
        max_length=10,
        choices=Tipo.choices,
        verbose_name="Tipo",
    )
    zone = models.CharField(max_length=20, verbose_name="Zona")
    date = models.DateField(verbose_name="Data")
    time = models.TimeField(verbose_name="Horário")
    pallets = models.PositiveIntegerField(verbose_name="Quantidade de Pallets")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDADO,
        verbose_name="Status",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "agendamentos"
        ordering = ["date", "time"]
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"

    def __str__(self):
        return f"{self.plate} – {self.date} {self.time} ({self.type})"
