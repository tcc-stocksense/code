from datetime import date

from pydantic import BaseModel


class MetricasModelo(BaseModel):
    """Métricas de avaliação de um modelo de séries temporais."""

    mape: float
    rmse: float
    mae: float


class PrevisaoDiaria(BaseModel):
    """Quantidade prevista para um único dia."""

    data: date
    quantidade_prevista: float


class PredictResponse(BaseModel):
    """Payload de saída do endpoint POST /predict."""

    produto_id: int
    modelo_selecionado: str
    previsoes: list[PrevisaoDiaria]
    metricas: dict[str, MetricasModelo]
    ponto_reposicao: float
    estoque_seguranca: float
    dias_ate_ruptura: float | None
    desvio_padrao_demanda: float
    aviso: str | None = None
