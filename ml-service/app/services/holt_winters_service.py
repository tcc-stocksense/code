"""
Implementação do modelo Holt-Winters (suavização exponencial tripla)
para o motor preditivo do StockSense.

Expõe apenas a função pública treinar_e_avaliar, seguindo o contrato
definido no CLAUDE.md do ml-service.
"""
import logging

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from app.models.predict_response import MetricasModelo

logger = logging.getLogger(__name__)

_SEASONAL_PERIODS: int = 7
_FORECAST_HORIZON: int = 30
_TRAIN_RATIO: float = 0.80
_MIN_OBSERVACOES: int = 10
_ZEROS_THRESHOLD: float = 0.30


def treinar_e_avaliar(serie: pd.Series) -> tuple[MetricasModelo, pd.Series]:
    """
    Treina o modelo Holt-Winters e retorna métricas de validação e previsão.

    Aplica validação walk-forward com divisão 80 % treino / 20 % validação
    para calcular as métricas. O modelo final é retreinado na série completa
    antes de gerar a previsão dos próximos 30 dias.

    Args:
        serie: Série temporal diária com DatetimeIndex e valores de quantidade
               vendida. Pode conter zeros (domingos, feriados). Mínimo de
               10 observações não-nulas exigido.

    Returns:
        metricas: Objeto MetricasModelo com MAPE, RMSE e MAE calculados
                  sobre o período de validação (últimos 20 % da série).
        previsao: pd.Series com DatetimeIndex diário continuando a partir
                  do último dia da série, com 30 valores não-negativos.

    Raises:
        ValueError: Quando a série tem menos de 10 observações não-nulas.
        RuntimeError: Quando o statsmodels falha ao ajustar o modelo.
    """
    _validar_serie(serie)

    proporcao_zeros = float((serie == 0).mean())
    if proporcao_zeros > _ZEROS_THRESHOLD:
        logger.warning(
            "Série com %.0f%% de zeros — qualidade da previsão pode ser reduzida",
            proporcao_zeros * 100,
        )

    usar_sazonalidade = len(serie) >= 2 * _SEASONAL_PERIODS
    if not usar_sazonalidade:
        logger.warning(
            "Série com apenas %d dias — sazonalidade semanal desabilitada (mínimo: %d dias)",
            len(serie),
            2 * _SEASONAL_PERIODS,
        )

    metricas = _walkforward(serie, usar_sazonalidade)
    previsao = _gerar_previsao(serie, usar_sazonalidade)
    return metricas, previsao


def _validar_serie(serie: pd.Series) -> None:
    """
    Verifica se a série tem observações suficientes para treinar o modelo.

    Args:
        serie: Série temporal a validar.

    Raises:
        ValueError: Quando há menos de 10 observações com quantidade > 0.
    """
    nao_nulas = int((serie > 0).sum())
    if nao_nulas < _MIN_OBSERVACOES:
        raise ValueError(
            f"Série insuficiente para Holt-Winters: {nao_nulas} observações "
            f"não-nulas (mínimo: {_MIN_OBSERVACOES})."
        )


def _ajustar_modelo(serie: pd.Series, usar_sazonalidade: bool) -> object:
    """
    Ajusta o modelo ExponentialSmoothing na série recebida.

    Configura tendência aditiva e sazonalidade aditiva com ciclo semanal
    (seasonal_periods=7) quando a série tem pelo menos dois ciclos completos.
    Desabilita a sazonalidade automaticamente em séries curtas para evitar
    erro do statsmodels.

    Args:
        serie: Série a ser ajustada.
        usar_sazonalidade: True quando len(serie) >= 14.

    Returns:
        Resultado ajustado do ExponentialSmoothing (HoltWintersResultsWrapper).

    Raises:
        RuntimeError: Quando o statsmodels não consegue convergir.
    """
    try:
        modelo = ExponentialSmoothing(
            serie,
            trend="add",
            seasonal="add" if usar_sazonalidade else None,
            seasonal_periods=_SEASONAL_PERIODS if usar_sazonalidade else None,
            initialization_method="estimated",
        )
        return modelo.fit(optimized=True, remove_bias=True)
    except Exception as exc:
        raise RuntimeError(
            f"Holt-Winters falhou ao ajustar o modelo: {exc}"
        ) from exc


def _calcular_metricas(real: np.ndarray, previsto: np.ndarray) -> MetricasModelo:
    """
    Calcula MAPE, RMSE e MAE entre valores reais e previstos.

    MAPE é computado apenas sobre observações com valor real > 0 para
    evitar divisão por zero em dias sem venda.

    Args:
        real: Array de valores observados no período de validação.
        previsto: Array de valores previstos pelo modelo no mesmo período.

    Returns:
        MetricasModelo com as três métricas arredondadas em 4 casas decimais.
    """
    mascara = real > 0
    if mascara.any():
        mape = float(
            np.mean(np.abs((real[mascara] - previsto[mascara]) / real[mascara])) * 100
        )
    else:
        mape = 0.0

    rmse = float(np.sqrt(mean_squared_error(real, previsto)))
    mae = float(mean_absolute_error(real, previsto))

    return MetricasModelo(
        mape=round(mape, 4),
        rmse=round(rmse, 4),
        mae=round(mae, 4),
    )


def _walkforward(serie: pd.Series, usar_sazonalidade: bool) -> MetricasModelo:
    """
    Avalia o modelo com validação walk-forward (80 % treino / 20 % validação).

    A sazonalidade é reavaliada sobre o tamanho do conjunto de treino para
    evitar erro quando a divisão 80/20 produz um treino com menos de 14 dias.

    Nunca usa train_test_split do scikit-learn — a divisão é feita por
    posição temporal para preservar a ordem cronológica da série.

    Args:
        serie: Série completa a ser dividida.
        usar_sazonalidade: Indicador calculado sobre a série completa;
                           reavaliado internamente para o conjunto de treino.

    Returns:
        MetricasModelo calculado sobre o conjunto de validação.
    """
    ponto_corte = int(len(serie) * _TRAIN_RATIO)
    treino = serie.iloc[:ponto_corte]
    validacao = serie.iloc[ponto_corte:]

    usar_sazonalidade_treino = usar_sazonalidade and len(treino) >= 2 * _SEASONAL_PERIODS
    modelo_ajustado = _ajustar_modelo(treino, usar_sazonalidade_treino)

    previsto = np.array(modelo_ajustado.forecast(len(validacao)))
    return _calcular_metricas(validacao.values, previsto)


def _gerar_previsao(serie: pd.Series, usar_sazonalidade: bool) -> pd.Series:
    """
    Retreina o modelo na série completa e gera a previsão de 30 dias.

    O retreino na série completa maximiza a qualidade da previsão final,
    aproveitando todos os dados disponíveis após a etapa de validação.

    Args:
        serie: Série completa usada para o treino final.
        usar_sazonalidade: Repassado para _ajustar_modelo.

    Returns:
        pd.Series com DatetimeIndex diário iniciando no dia seguinte ao
        último da série, contendo 30 valores não-negativos.
    """
    modelo_ajustado = _ajustar_modelo(serie, usar_sazonalidade)
    previsao = modelo_ajustado.forecast(_FORECAST_HORIZON)
    datas_futuras = pd.date_range(
        start=serie.index[-1] + pd.Timedelta(days=1),
        periods=_FORECAST_HORIZON,
        freq="D",
    )
    return pd.Series(
        np.maximum(np.array(previsao), 0.0),
        index=datas_futuras,
    )
