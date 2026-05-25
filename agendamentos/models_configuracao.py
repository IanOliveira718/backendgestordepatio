from django.db import models


class Configuracao(models.Model):
    """
    Tabela singleton — sempre haverá apenas um registro (pk=1).
    Use Configuracao.get() para acessar.
    """

    # Janela de tempo para verificação de capacidade de zona
    janela_dias  = models.PositiveIntegerField(
        default=0,
        verbose_name="Janela — dias",
        help_text="Número de dias antes/depois do agendamento a considerar no cálculo de capacidade.",
    )
    janela_horas = models.PositiveIntegerField(
        default=24,
        verbose_name="Janela — horas",
        help_text="Número de horas antes/depois do agendamento a considerar (somado aos dias).",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = "configuracoes"
        verbose_name = "Configuração do Sistema"

    def __str__(self):
        return f"Configuração — janela: {self.janela_dias}d {self.janela_horas}h"

    @classmethod
    def get(cls) -> "Configuracao":
        """Retorna (ou cria) o único registro de configuração."""
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"janela_dias": 0, "janela_horas": 24})
        return obj

    @property
    def janela_total_horas(self) -> int:
        return self.janela_dias * 24 + self.janela_horas
