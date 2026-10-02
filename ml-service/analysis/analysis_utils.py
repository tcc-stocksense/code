"""
Funções de apoio para o notebook de análise/validação empírica dos modelos
(analise_modelos.ipynb) do TCC StockSense.

Princípio central: **reaproveitar o código de produção**, nunca reimplementar
as fórmulas. As métricas MAPE/RMSE/MAE saem exatamente do mesmo código que o
motor usa em `/predict`, para que os números do TCC sejam idênticos aos do
sistema. Para os gráficos "previsto × real" precisamos, além das métricas, das
próprias previsões na janela de validação — algo que a função pública
`treinar_e_avaliar` não devolve. Por isso reutilizamos os *helpers* internos
`_ajustar_modelo` e `_calcular_metricas` de cada serviço, replicando o mesmo
split 80/20 walk-forward (mesma configuração → mesmos resultados).

Este módulo é um artefato de análise e vive fora do runtime do serviço.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Helpers internos dos serviços — reutilizados de propósito para garantir que a
# análise use exatamente a mesma configuração de modelo do motor em produção.
# O prophet_service é importado de forma *lazy* (dentro das funções), porque
# `import prophet` pode falhar no ambiente (T-12) — ver prophet_disponivel().
from app.services import holt_winters_service as hw
from app.models.predict_response import MetricasModelo

_TRAIN_RATIO: float = 0.80


# ─────────────────────────────────────────────────────────────────────────────
# Disponibilidade do Prophet (risco T-12: ambiente/CmdStan pode estar quebrado)
# ─────────────────────────────────────────────────────────────────────────────
def prophet_disponivel() -> bool:
    """
    Verifica se o Prophet consegue ser instanciado neste ambiente.

    O `tasks.md` (T-12) registra que o backend do Prophet (CmdStan) pode estar
    quebrado no venv. Esta checagem permite o notebook degradar para apenas
    Holt-Winters em vez de falhar, sinalizando a limitação de forma honesta.

    Returns:
        True se `from prophet import Prophet` e a instância funcionarem.
    """
    try:
        from prophet import Prophet  # noqa: F401

        Prophet()
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Split temporal (nunca aleatório — ver CLAUDE.md §6 e §15 do ml-service)
# ─────────────────────────────────────────────────────────────────────────────
def split_temporal(
    serie: pd.Series, ratio: float = _TRAIN_RATIO
) -> tuple[pd.Series, pd.Series]:
    """
    Divide a série por posição cronológica (walk-forward), nunca embaralhando.

    Args:
        serie: Série temporal diária com DatetimeIndex.
        ratio: Fração inicial usada para treino (padrão 0.80, igual ao motor).

    Returns:
        (treino, validacao) — os primeiros `ratio` da série e o restante.
    """
    ponto_corte = int(len(serie) * ratio)
    return serie.iloc[:ponto_corte], serie.iloc[ponto_corte:]


def _resultado(
    treino: pd.Series,
    validacao: pd.Series,
    previsto: np.ndarray,
    metricas: MetricasModelo,
) -> dict:
    """Empacota o resultado de uma avaliação walk-forward para o notebook."""
    return {
        "treino": treino,
        "validacao": validacao,
        "previsto": pd.Series(previsto, index=validacao.index),
        "metricas": metricas,
    }


def avaliar_holt_winters(serie: pd.Series) -> dict:
    """
    Avalia Holt-Winters na janela de validação, devolvendo previsões + métricas.

    Reproduz fielmente o `_walkforward` do serviço (mesmo split, mesma
    configuração de sazonalidade, sem *clamp* nas métricas), acrescentando a
    série prevista para permitir o gráfico previsto × real.

    Args:
        serie: Série temporal diária com DatetimeIndex.

    Returns:
        dict com chaves: treino, validacao, previsto (pd.Series), metricas.
    """
    treino, validacao = split_temporal(serie)
    usar_saz = len(treino) >= 2 * hw._SEASONAL_PERIODS
    modelo = hw._ajustar_modelo(treino, usar_saz)
    previsto = np.array(modelo.forecast(len(validacao)))
    metricas = hw._calcular_metricas(validacao.values, previsto)
    return _resultado(treino, validacao, previsto, metricas)


def avaliar_prophet(serie: pd.Series) -> dict:
    """
    Avalia Prophet na janela de validação, devolvendo previsões + métricas.

    Espelha o `_walkforward` do prophet_service. Só deve ser chamada quando
    `prophet_disponivel()` for True.

    Args:
        serie: Série temporal diária com DatetimeIndex.

    Returns:
        dict com chaves: treino, validacao, previsto (pd.Series), metricas.
    """
    from app.services import prophet_service as _pr_module

    treino, validacao = split_temporal(serie)
    usar_saz = len(treino) >= 2 * _pr_module._SEASONAL_PERIODS
    modelo = _pr_module._ajustar_modelo(treino, usar_saz)
    forecast = modelo.predict(pd.DataFrame({"ds": validacao.index}))
    previsto = forecast["yhat"].values
    metricas = _pr_module._calcular_metricas(validacao.values, previsto)
    return _resultado(treino, validacao, previsto, metricas)


# ─────────────────────────────────────────────────────────────────────────────
# Backtesting rolling-origin (robustez ao longo de várias janelas)
# ─────────────────────────────────────────────────────────────────────────────
def backtesting_rolling(
    serie: pd.Series,
    avaliador,
    n_janelas: int = 5,
    tamanho_teste: int = 14,
) -> pd.DataFrame:
    """
    Avaliação rolling-origin: repete o treino/teste em várias janelas móveis.

    Em cada dobra, o treino cresce (origem expansível) e a previsão é feita
    sobre o bloco de teste seguinte. Mostra que o desempenho é consistente e
    não fruto de uma única divisão sortuda.

    Args:
        serie: Série temporal diária.
        avaliador: Função que ajusta o modelo no treino e prevê o teste,
                   assinatura `(treino, validacao) -> np.ndarray` (previsto).
        n_janelas: Número de dobras.
        tamanho_teste: Dias em cada bloco de teste.

    Returns:
        DataFrame com uma linha por dobra: origem, mape, rmse, mae.
    """
    linhas = []
    total = len(serie)
    for k in range(n_janelas, 0, -1):
        fim_treino = total - k * tamanho_teste
        if fim_treino < 2 * hw._SEASONAL_PERIODS:
            continue
        treino = serie.iloc[:fim_treino]
        validacao = serie.iloc[fim_treino:fim_treino + tamanho_teste]
        previsto = avaliador(treino, validacao)
        m = hw._calcular_metricas(validacao.values, np.asarray(previsto))
        linhas.append(
            {
                "origem": serie.index[fim_treino].date().isoformat(),
                "mape": m.mape,
                "rmse": m.rmse,
                "mae": m.mae,
            }
        )
    return pd.DataFrame(linhas)


def prever_hw(treino: pd.Series, validacao: pd.Series) -> np.ndarray:
    """Adaptador de previsão Holt-Winters para o backtesting_rolling."""
    usar_saz = len(treino) >= 2 * hw._SEASONAL_PERIODS
    modelo = hw._ajustar_modelo(treino, usar_saz)
    return np.array(modelo.forecast(len(validacao)))


def prever_prophet(treino: pd.Series, validacao: pd.Series) -> np.ndarray:
    """Adaptador de previsão Prophet para o backtesting_rolling."""
    from app.services import prophet_service as _pr_module

    usar_saz = len(treino) >= 2 * _pr_module._SEASONAL_PERIODS
    modelo = _pr_module._ajustar_modelo(treino, usar_saz)
    forecast = modelo.predict(pd.DataFrame({"ds": validacao.index}))
    return forecast["yhat"].values


# ─────────────────────────────────────────────────────────────────────────────
# Dataset real (.xlsx no formato do Guia de Importação v2.0 — planilha 5_vendas)
# ─────────────────────────────────────────────────────────────────────────────
def carregar_series_reais(
    caminho: str | Path,
    coluna_produto: str = "produto_id",
    coluna_data: str = "data_hora",
    coluna_qtd: str = "quantidade",
) -> dict[int, pd.Series]:
    """
    Lê uma planilha real de vendas e devolve uma série diária por produto.

    Espera o formato da planilha `5_vendas` (Guia de Importação v2.0):
    colunas `produto_id`, `data_hora` (YYYY-MM-DD[ HH:MM:SS]) e `quantidade`.
    Agrega por dia, reindexa em frequência diária contínua e preenche os dias
    sem venda com zero — do mesmo jeito que o dataset sintético mantém os zeros,
    para preservar a continuidade temporal exigida pelos modelos.

    Args:
        caminho: Caminho do arquivo .xlsx real.
        coluna_produto / coluna_data / coluna_qtd: nomes das colunas, caso o
            arquivo real use variações.

    Returns:
        dict produto_id → pd.Series (DatetimeIndex diário contínuo, com zeros).

    Raises:
        FileNotFoundError: Se o arquivo não existir.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(caminho)

    df = pd.read_excel(caminho)
    df[coluna_data] = pd.to_datetime(df[coluna_data]).dt.normalize()

    series: dict[int, pd.Series] = {}
    for produto_id, grupo in df.groupby(coluna_produto):
        diario = grupo.groupby(coluna_data)[coluna_qtd].sum().sort_index()
        indice = pd.date_range(diario.index.min(), diario.index.max(), freq="D")
        series[int(produto_id)] = diario.reindex(indice, fill_value=0).astype(float)
    return series


# ─────────────────────────────────────────────────────────────────────────────
# Baseline ingênuo sazonal — referência de comparação, NÃO faz parte do motor
# ─────────────────────────────────────────────────────────────────────────────
# Vive na camada de análise de propósito: é instrumento de avaliação, não um
# terceiro modelo candidato. O motor em produção continua escolhendo apenas
# entre Holt-Winters e Prophet; o ingênuo serve para responder se essa escolha
# entrega ganho sobre uma regra que não estima parâmetro nenhum.
_PERIODO_SAZONAL: int = 7


def prever_naive_sazonal(
    treino: pd.Series,
    validacao: pd.Series,
    periodo: int = _PERIODO_SAZONAL,
) -> np.ndarray:
    """
    Previsão ingênua sazonal: repete o último ciclo semanal observado no treino.

    Formalmente, ŷ(T+h) = y(T + h − m·⌈h/m⌉), com m = 7 (Hyndman e
    Athanasopoulos, 2021): cada dia previsto recebe o valor do mesmo dia da
    semana na última semana completa do conjunto de treino.

    Args:
        treino: Série de treino (DatetimeIndex diário).
        validacao: Série de validação — só o comprimento é usado.
        periodo: Tamanho do ciclo sazonal em dias (padrão 7).

    Returns:
        np.ndarray com uma previsão por dia da janela de validação.
    """
    ultimo_ciclo = np.asarray(treino.values[-periodo:], dtype=float)
    n_previsoes = len(validacao)
    repeticoes = int(np.ceil(n_previsoes / periodo))
    return np.tile(ultimo_ciclo, repeticoes)[:n_previsoes]


def avaliar_naive_sazonal(serie: pd.Series) -> dict:
    """
    Avalia o baseline ingênuo na mesma janela de validação dos modelos.

    Usa o mesmo split 80/20 e o mesmo `_calcular_metricas` do motor, para que
    o MAPE do ingênuo seja comparável ao dos modelos sem nenhuma ressalva
    metodológica.

    Args:
        serie: Série temporal diária com DatetimeIndex.

    Returns:
        dict com chaves: treino, validacao, previsto (pd.Series), metricas.
    """
    treino, validacao = split_temporal(serie)
    previsto = prever_naive_sazonal(treino, validacao)
    metricas = hw._calcular_metricas(validacao.values, previsto)
    return _resultado(treino, validacao, previsto, metricas)


def treinar_e_avaliar_naive(serie: pd.Series) -> tuple[MetricasModelo, pd.Series]:
    """
    Espelha a assinatura de `treinar_e_avaliar` dos serviços de produção.

    Permite tratar o baseline como um "modelo" nos laços de comparação do
    notebook, sem que ele entre na disputa pelo vencedor. A previsão final
    repete o último ciclo semanal da série completa, pelo mesmo horizonte de
    30 dias adotado pelo motor.

    Args:
        serie: Série temporal diária com DatetimeIndex.

    Returns:
        metricas: MetricasModelo da janela de validação (split 80/20).
        previsao: pd.Series de 30 dias iniciando no dia seguinte ao último.
    """
    metricas = avaliar_naive_sazonal(serie)["metricas"]

    horizonte = hw._FORECAST_HORIZON
    ultimo_ciclo = np.asarray(serie.values[-_PERIODO_SAZONAL:], dtype=float)
    valores = np.tile(
        ultimo_ciclo, int(np.ceil(horizonte / _PERIODO_SAZONAL))
    )[:horizonte]
    indice = pd.date_range(
        serie.index.max() + pd.Timedelta(days=1), periods=horizonte, freq="D"
    )
    return metricas, pd.Series(valores, index=indice)
