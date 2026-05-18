from datetime import date

from pydantic import BaseModel, Field


class VendaDiaria(BaseModel):
    """Registro de venda de um único dia."""

    data: date
    quantidade: int = Field(gt=0)


class PredictRequest(BaseModel):
    """Payload de entrada para o endpoint POST /predict."""

    produto_id: int
    historico: list[VendaDiaria] = Field(min_length=90)
    lead_time_medio: int = Field(default=3, ge=1)
    variabilidade_lead_time: float = Field(default=1.0, ge=0)
    nivel_servico_alvo: float = Field(default=0.95, ge=0.5, le=0.999)
    estoque_atual: int = Field(ge=0)
    is_promocional: list[int] = Field(default_factory=list)
