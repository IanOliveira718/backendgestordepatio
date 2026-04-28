from django.db import models


class Patio(models.Model):
    nome      = models.CharField(max_length=100, verbose_name="Nome do Pátio")
    localizacao = models.CharField(max_length=255, verbose_name="Localização")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = "patios"
        ordering            = ["nome"]
        verbose_name        = "Pátio"
        verbose_name_plural = "Pátios"

    def __str__(self):
        return self.nome


class Zona(models.Model):
    class TipoZona(models.TextChoices):
        PRINCIPAL    = "principal",    "Principal"
        REFRIGERADA  = "refrigerada",  "Refrigerada"
        EXPEDICAO    = "expedicao",    "Expedição"
        RECEBIMENTO  = "recebimento",  "Recebimento"
        RESERVA      = "reserva",      "Reserva"
        AVARIADO     = "avariado",     "Avariado"

    patio       = models.ForeignKey(
        Patio,
        on_delete=models.CASCADE,
        related_name="zonas",
        verbose_name="Pátio",
    )
    nome        = models.CharField(max_length=50,  verbose_name="Nome da Zona")
    tipo        = models.CharField(
        max_length=20,
        choices=TipoZona.choices,
        verbose_name="Tipo da Zona",
    )
    capacidade  = models.PositiveIntegerField(verbose_name="Capacidade (pallets)")
    localizacao = models.CharField(max_length=255, verbose_name="Localização", blank=True, default="")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = "zonas"
        ordering            = ["patio", "nome"]
        verbose_name        = "Zona"
        verbose_name_plural = "Zonas"

    def __str__(self):
        return f"{self.patio.nome} — {self.nome} ({self.tipo})"
