from django.db import models


class Agendamento(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SAIDA   = "saida",   "Saída"

    class Status(models.TextChoices):
        AGENDADO     = "agendado",     "Agendado"
        CONFIRMADO   = "confirmado",   "Confirmado"
        EM_ANDAMENTO = "em_andamento", "Em Andamento"
        CONCLUIDO    = "concluido",    "Concluído"
        CANCELADO    = "cancelado",    "Cancelado"

    class TipoUnidade(models.TextChoices):
        PALLET = "pallet", "Pallet"
        VOLUME = "volume", "Volume"

    plate        = models.CharField(max_length=20,  verbose_name="Placa")
    driver       = models.CharField(max_length=150, verbose_name="Motorista")
    type         = models.CharField(max_length=10, choices=Tipo.choices, verbose_name="Tipo")
    zone         = models.CharField(max_length=20, verbose_name="Zona")
    date         = models.DateField(verbose_name="Data")
    time         = models.TimeField(verbose_name="Horário")

    # quantidade prevista de pallets
    pallets      = models.PositiveIntegerField(verbose_name="Quantidade de Unidades")

    nota_fiscal  = models.CharField(max_length=60, verbose_name="Nota Fiscal")

    tipo_unidade = models.CharField(
        max_length=10,
        choices=TipoUnidade.choices,
        default=TipoUnidade.PALLET,
        verbose_name="Tipo de Unidade",
    )

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


class PalletDescricao(models.Model):
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name="descricoes_pallets"
    )

    ordem     = models.PositiveSmallIntegerField(verbose_name="Ordem do Pallet")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")

    class Meta:
        db_table = "pallet_descricoes"
        ordering = ["agendamento", "ordem"]
        unique_together = (("agendamento", "ordem"),)

    def __str__(self):
        return f"Pallet {self.ordem}"


class VolumeDescricao(models.Model):
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name="descricoes_volumes"
    )

    ordem       = models.PositiveSmallIntegerField(verbose_name="Ordem do Volume")
    descricao   = models.CharField(max_length=255, verbose_name="Descrição")
    altura      = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Altura (cm)")
    largura     = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Largura (cm)")
    comprimento = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Comprimento (cm)")

    class Meta:
        db_table = "volume_descricoes"
        ordering = ["agendamento", "ordem"]
        unique_together = (("agendamento", "ordem"),)

    def __str__(self):
        return f"Volume {self.ordem}"


class Pallet(models.Model):
    """
    Um registro por pallet físico criado ao confirmar um agendamento.
    """

    class Status(models.TextChoices):
        PENDENTE   = "pendente",   "Pendente"
        ARMAZENADO = "armazenado", "Armazenado"
        RETIRADO   = "retirado",   "Retirado"
        AVARIADO   = "avariado",   "Avariado"

    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name="pallet_registrados",  # ✅ corrigido aqui
        verbose_name="Agendamento",
    )

    numero_pallet = models.PositiveIntegerField(verbose_name="Número do Pallet")
    numero_espaco = models.PositiveIntegerField(verbose_name="Número do Espaço")
    zona_nome     = models.CharField(max_length=50, verbose_name="Zona")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name="Status",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pallets"
        ordering = ["agendamento", "numero_pallet"]
        unique_together = (("agendamento", "numero_pallet"),)
        verbose_name = "Pallet"
        verbose_name_plural = "Pallets"

    def __str__(self):
        return f"Pallet {self.numero_pallet} — Espaço {self.numero_espaco} ({self.zona_nome})"