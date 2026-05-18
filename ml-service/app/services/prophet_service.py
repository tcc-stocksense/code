"""
Implementação do modelo Prophet (Meta) para o motor preditivo do StockSense.

Expõe apenas a função pública treinar_e_avaliar, seguindo o mesmo contrato
do holt_winters_service e definido no CLAUDE.md do ml-service.

A renomeação das colunas para o formato ds/y exigido pelo Prophet é feita
exclusivamente dentro deste módulo — nunca fora dele.
"""
import logging

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.models.predict_response import MetricasModelo

logger = logging.getLogger(__name__)

# Suprime output verboso do Prophet e do CmdStanPy durante o ajuste do modelo
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

_SEASONAL_PERIODS: int = 7
_FORECAST_HORIZON: int = 30
_TRAIN_RATIO: float = 0.80
_MIN_OBSERVACOES: int = 10
_ZEROS_THRESHOLD: float = 0.30


def treinar_e_avaliar(serie: pd.Series) -> tuple[MetricasModelo, pd.Series]:
    """
    Treina o modelo Prophet e retorna métricas de validação e previsão.

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
        RuntimeError: Quando o Prophet falha ao ajustar o modelo.
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
            f"Série insuficiente para Prophet: {nao_nulas} observações "
            f"não-nulas (mínimo: {_MIN_OBSERVACOES})."
        )


def _converter_para_prophet_df(serie: pd.Series) -> pd.DataFrame:
    """
    Converte pd.Series com DatetimeIndex para o formato exigido pelo Prophet.

    A renomeação para ds/y ocorre exclusivamente aqui — o restante do
    serviço trabalha com pd.Series nativas.

    Args:
        serie: Série temporal com DatetimeIndex.

    Returns:
        DataFrame com colunas ds (datas) e y (quantidades).
    """
    return pd.DataFrame({"ds": serie.index, "y": serie.values})


def _ajustar_modelo(serie: pd.Series, usar_sazonalidade: bool) -> Prophet:
    """
    Instancia e ajusta o modelo Prophet com os hiperparâmetros do projeto.

    Configura sazonalidade anual desabilitada (90 dias insuficientes para
    capturar ciclo anual), sazonalidade semanal habilitada quando a série
    tem ao menos dois ciclos completos (14 dias) e sazonalidade diária
    desabilitada (granularidade já é diária).

    Args:
        serie: Série a ser ajustada.
        usar_sazonalidade: True quando len(serie) >= 14.

    Returns:
        Modelo Prophet ajustado.

    Raises:
        RuntimeError: Quando o Prophet falha ao convergir.
    """
    try:
        modelo = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=usar_sazonalidade,
            daily_seasonality=False,
            interval_width=0.95,
        )
        modelo.fit(_converter_para_prophet_df(serie))
        return modelo
    except Exception as exc:
        raise RuntimeError(
            f"Prophet falhou ao ajustar o modelo: {exc}"
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
    evitar problemas quando a divisão 80/20 produz um treino com menos de
    14 dias.

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
    modelo = _ajustar_modelo(treino, usar_sazonalidade_treino)

    future = pd.DataFrame({"ds": validacao.index})
    forecast = modelo.predict(future)
    previsto = forecast["yhat"].values

    return _calcular_metricas(validacao.values, previsto)


def _gerar_previsao(serie: pd.Series, usar_sazonalidade: bool) -> pd.Series:
    """
    Retreina o modelo na série completa e gera a previsão de 30 dias.

    As datas futuras são construídas explicitamente a partir do dia seguinte
    ao último da série, evitando ambiguidade com make_future_dataframe.

    Args:
        serie: Série completa usada para o treino final.
        usar_sazonalidade: Repassado para _ajustar_modelo.

    Returns:
        pd.Series com DatetimeIndex diário iniciando no dia seguinte ao
        último da série, contendo 30 valores não-negativos.
    """
    modelo = _ajustar_modelo(serie, usar_sazonalidade)

    datas_futuras = pd.date_range(
        start=serie.index[-1] + pd.Timedelta(days=1),
        periods=_FORECAST_HORIZON,
        freq="D",
    )
    forecast = modelo.predict(pd.DataFrame({"ds": datas_futuras}))

    yhat = np.maximum(forecast["yhat"].values, 0.0)
    return pd.Series(yhat, index=datas_futuras)
