"""
Orquestrador central do motor preditivo do StockSense.

Coordena os modelos Holt-Winters e Prophet, seleciona o vencedor por MAPE
e calcula os KPIs de estoque para um único produto.
"""
from __future__ import annotations

import logging

import pandas as pd

from app.models.predict_request import PredictRequest
from app.models.predict_response import MetricasModelo, PrevisaoDiaria, PredictResponse
from app.services import holt_winters_service, prophet_service
from app.services.stock_service import (
    calcular_dias_ate_ruptura,
    calcular_estoque_seguranca,
    calcular_ponto_reposicao,
    calcular_z_score,
)

logger = logging.getLogger(__name__)

_MAPE_AVISO_LIMIAR: float = 50.0


async def executar_previsao(request: PredictRequest) -> PredictResponse:
    """
    Orquestra o fluxo completo de previsão e cálculo de KPIs para um produto.

    Prepara a série temporal, treina Holt-Winters e Prophet em paralelo lógico
    (tolerando falha individual), seleciona o modelo de menor MAPE e calcula os
    KPIs de estoque pela fórmula de Ballou (2006).

    Args:
        request: Payload validado do endpoint POST /predict.

    Returns:
        PredictResponse com previsões dos próximos 30 dias, métricas
        comparativas dos dois modelos e todos os KPIs de estoque.

    Raises:
        RuntimeError: Quando ambos os modelos falham ao treinar.
    """
    pid = request.produto_id
    logger.info("[produto_id=%d] Iniciando previsão", pid)

    serie = _preparar_serie(request)

    metricas_hw, previsao_hw, erro_hw = _tentar_holt_winters(serie, pid)
    metricas_prophet, previsao_prophet, erro_prophet = _tentar_prophet(serie, pid)

    if metricas_hw is None and metricas_prophet is None:
        raise RuntimeError(
            f"[produto_id={pid}] Ambos os modelos falharam. "
            f"Holt-Winters: {erro_hw}. Prophet: {erro_prophet}."
        )

    modelo_selecionado, previsao_vencedora, metricas_vencedor = _selecionar_modelo(
        metricas_hw, previsao_hw, metricas_prophet, previsao_prophet
    )

    logger.info(
        "[produto_id=%d] Holt-Winters MAPE=%.2f%% | Prophet MAPE=%.2f%% | Selecionado: %s",
        pid,
        metricas_hw.mape if metricas_hw is not None else float("inf"),
        metricas_prophet.mape if metricas_prophet is not None else float("inf"),
        modelo_selecionado,
    )

    metricas: dict[str, MetricasModelo] = {}
    if metricas_hw is not None:
        metricas["holt_winters"] = metricas_hw
    if metricas_prophet is not None:
        metricas["prophet"] = metricas_prophet

    previsoes = [
        PrevisaoDiaria(data=ts.date(), quantidade_prevista=round(float(qtd), 4))
        for ts, qtd in previsao_vencedora.items()
    ]

    demanda_media = float(previsao_vencedora.mean())
    desvio_demanda = float(serie.std())

    z = calcular_z_score(request.nivel_servico_alvo)
    estoque_seguranca = calcular_estoque_seguranca(
        z=z,
        lead_time_medio=request.lead_time_medio,
        desvio_demanda=desvio_demanda,
        demanda_media=demanda_media,
        variabilidade_lead_time=request.variabilidade_lead_time,
    )
    ponto_reposicao = calcular_ponto_reposicao(
        demanda_media=demanda_media,
        lead_time_medio=request.lead_time_medio,
        estoque_seguranca=estoque_seguranca,
    )
    dias_ate_ruptura = calcular_dias_ate_ruptura(
        estoque_atual=request.estoque_atual,
        demanda_media_diaria=demanda_media,
    )

    aviso: str | None = None
    if metricas_vencedor.mape > _MAPE_AVISO_LIMIAR:
        aviso = "Acurácia baixa — previsões com confiança reduzida"
        logger.warning(
            "[produto_id=%d] MAPE=%.2f%% acima de %.0f%% — aviso incluído na resposta",
            pid,
            metricas_vencedor.mape,
            _MAPE_AVISO_LIMIAR,
        )

    logger.info("[produto_id=%d] Modelo selecionado: %s", pid, modelo_selecionado)

    return PredictResponse(
        produto_id=pid,
        modelo_selecionado=modelo_selecionado,
        previsoes=previsoes,
        metricas=metricas,
        ponto_reposicao=round(ponto_reposicao, 4),
        estoque_seguranca=round(estoque_seguranca, 4),
        dias_ate_ruptura=round(dias_ate_ruptura, 4) if dias_ate_ruptura is not None else None,
        desvio_padrao_demanda=round(desvio_demanda, 4),
        aviso=aviso,
    )


def _preparar_serie(request: PredictRequest) -> pd.Series:
    """
    Converte o histórico do PredictRequest em pd.Series com DatetimeIndex.

    Ordena cronologicamente para garantir que a divisão walk-forward seja
    sempre temporal, independentemente da ordem de chegada no payload.

    Args:
        request: Payload validado com campo historico.

    Returns:
        Série diária ordenada cronologicamente com DatetimeIndex e dtype float.
    """
    datas = [v.data for v in request.historico]
    quantidades = [float(v.quantidade) for v in request.historico]
    serie = pd.Series(quantidades, index=pd.DatetimeIndex(datas), dtype=float)
    return serie.sort_index()


def _tentar_holt_winters(
    serie: pd.Series,
    produto_id: int,
) -> tuple[MetricasModelo | None, pd.Series | None, str | None]:
    """
    Executa o Holt-Winters capturando exceções sem interromper o fluxo.

    Returns:
        (metricas, previsao, mensagem_erro) — erro é None quando bem-sucedido.
    """
    try:
        metricas, previsao = holt_winters_service.treinar_e_avaliar(serie)
        return metricas, previsao, None
    except Exception as exc:
        logger.warning("[produto_id=%d] Holt-Winters descartado: %s", produto_id, exc)
        return None, None, str(exc)


def _tentar_prophet(
    serie: pd.Series,
    produto_id: int,
) -> tuple[MetricasModelo | None, pd.Series | None, str | None]:
    """
    Executa o Prophet capturando exceções sem interromper o fluxo.

    Returns:
        (metricas, previsao, mensagem_erro) — erro é None quando bem-sucedido.
    """
    try:
        metricas, previsao = prophet_service.treinar_e_avaliar(serie)
        return metricas, previsao, None
    except Exception as exc:
        logger.warning("[produto_id=%d] Prophet descartado: %s", produto_id, exc)
        return None, None, str(exc)


def _selecionar_modelo(
    metricas_hw: MetricasModelo | None,
    previsao_hw: pd.Series | None,
    metricas_prophet: MetricasModelo | None,
    previsao_prophet: pd.Series | None,
) -> tuple[str, pd.Series, MetricasModelo]:
    """
    Seleciona o modelo vencedor pelo menor MAPE.

    Quando apenas um modelo está disponível (o outro falhou), ele é
    selecionado sem comparação. O chamador garante que pelo menos um
    par (metricas, previsao) não é None antes de chamar esta função.

    Args:
        metricas_hw: Métricas do Holt-Winters, ou None se falhou.
        previsao_hw: Previsão do Holt-Winters, ou None se falhou.
        metricas_prophet: Métricas do Prophet, ou None se falhou.
        previsao_prophet: Previsão do Prophet, ou None se falhou.

    Returns:
        Tupla (nome_modelo, serie_previsao, metricas_vencedor).
    """
    if metricas_hw is None:
        return "prophet", previsao_prophet, metricas_prophet  # type: ignore[return-value]
    if metricas_prophet is None:
        return "holt_winters", previsao_hw, metricas_hw  # type: ignore[return-value]

    if metricas_hw.mape <= metricas_prophet.mape:
        return "holt_winters", previsao_hw, metricas_hw
    return "prophet", previsao_prophet, metricas_prophet
