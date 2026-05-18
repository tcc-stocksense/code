"""
Fixtures compartilhadas entre todos os testes do ml-service.
"""
import numpy as np
import pandas as pd
import pytest

_FATOR_SEMANA = {0: 0.85, 1: 0.75, 2: 0.80, 3: 0.90, 4: 1.35, 5: 1.45, 6: 0.30}


@pytest.fixture(scope="session")
def serie_90_dias() -> pd.Series:
    """
    Série temporal diária de 90 dias com sazonalidade semanal sintética.

    Gerada com semente fixa para garantir reprodutibilidade entre execuções.
    Representa um produto de demanda estável (ex: Arroz).
    """
    rng = np.random.default_rng(42)
    datas = pd.date_range(start="2024-01-01", periods=90, freq="D")
    fatores = np.array([_FATOR_SEMANA[d.dayofweek] for d in datas])
    ruido = rng.normal(1.0, 0.15, size=90)
    quantidades = np.maximum(np.round(15.0 * fatores * ruido), 0.0)
    return pd.Series(quantidades, index=datas)


@pytest.fixture
def serie_curta() -> pd.Series:
    """
    Série com 10 dias — abaixo dos 14 necessários para sazonalidade semanal.

    Deve acionar o fallback para seasonal=None no Holt-Winters e no Prophet.
    """
    datas = pd.date_range(start="2024-01-01", periods=10, freq="D")
    quantidades = [10.0, 12.0, 8.0, 14.0, 18.0, 11.0, 6.0, 13.0, 10.0, 12.0]
    return pd.Series(quantidades, index=datas)


@pytest.fixture
def serie_com_zeros_excessivos() -> pd.Series:
    """
    Série de 90 dias com 35 % de zeros — acima do limiar de 30 %.

    Deve emitir aviso de log e continuar o processamento normalmente.
    """
    rng = np.random.default_rng(42)
    datas = pd.date_range(start="2024-01-01", periods=90, freq="D")
    quantidades = rng.integers(5, 30, size=90).astype(float)
    indices_zero = rng.choice(90, size=32, replace=False)
    quantidades[indices_zero] = 0.0
    return pd.Series(quantidades, index=datas)


@pytest.fixture
def payload_valido() -> dict:
    """
    Payload mínimo válido para POST /predict com 90 dias de histórico.
    """
    datas = pd.date_range(start="2024-01-01", periods=90, freq="D")
    return {
        "produto_id": 1,
        "historico": [
            {"data": str(d.date()), "quantidade": 10 + i % 5}
            for i, d in enumerate(datas)
        ],
        "lead_time_medio": 3,
        "variabilidade_lead_time": 1.0,
        "nivel_servico_alvo": 0.95,
        "estoque_atual": 40,
    }
