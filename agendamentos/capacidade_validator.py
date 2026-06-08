"""
Validador de capacidade de zona com janela de tempo configurável.

Regra:
  Para uma zona Z, data D e hora H:
  - Soma todos os pallets de agendamentos ativos (não cancelados) cuja
    data/hora esteja dentro da janela [D H - janela, D H + janela].
  - Agendamentos concluídos só entram se estiverem na janela ANTES (até 24h antes).
  - O total + pallets da solicitação corrente deve ser <= capacidade da zona.
"""

from datetime import datetime, timedelta
from django.db.models import Q, Sum
from typing import Optional

def verificar_capacidade(zona_nome: str, zona_capacidade: int,
                          qtd_pallets: int,
                          data_agendamento,   # date
                          hora_agendamento,   # time
                          excluir_agendamento_id=None) -> Optional[str]:
    """
    Retorna mensagem de erro se não houver capacidade, ou None se OK.
    """
    # Importações locais para evitar circular imports
    from agendamentos.models import Agendamento
    from agendamentos.models_configuracao import Configuracao

    config = Configuracao.get()
    janela = timedelta(hours=config.janela_total_horas)

    # Datetime do agendamento sendo criado/validado
    dt_ref = datetime.combine(data_agendamento, hora_agendamento)
    dt_min = dt_ref - janela
    dt_max = dt_ref + janela

    # Base: agendamentos da mesma zona, não cancelados
    qs = Agendamento.objects.filter(zone=zona_nome).exclude(
        status=Agendamento.Status.CANCELADO
    )

    if excluir_agendamento_id:
        qs = qs.exclude(pk=excluir_agendamento_id)

    # Filtra pela janela de tempo usando anotação de datetime combinado
    # Django não tem DateTimeField combinado nativamente, então filtramos em Python
    agendamentos_janela = []
    for ag in qs.only("id", "date", "time", "pallets", "status"):
        dt_ag = datetime.combine(ag.date, ag.time)

        # Concluídos: só contam se estão na janela ANTES (não depois)
        if ag.status == Agendamento.Status.CONCLUIDO:
            if dt_min <= dt_ag <= dt_ref:
                agendamentos_janela.append(ag)
        else:
            # Ativos (agendado, confirmado, em_andamento): janela completa
            if dt_min <= dt_ag <= dt_max:
                agendamentos_janela.append(ag)

    total_na_janela = sum(ag.pallets for ag in agendamentos_janela)
    total_com_novo  = total_na_janela + qtd_pallets

    if total_com_novo > zona_capacidade:
        disponivel = max(zona_capacidade - total_na_janela, 0)
        return (
            f"Capacidade insuficiente na zona {zona_nome}. "
            f"Capacidade total: {zona_capacidade} pallets. "
            f"Já ocupado na janela de {config.janela_dias}d {config.janela_horas}h: {total_na_janela}. "
            f"Disponível: {disponivel}. "
            f"Solicitado: {qtd_pallets}."
        )

    return None
