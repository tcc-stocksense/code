import logging

from fastapi import APIRouter, HTTPException

from app.models.predict_request import PredictRequest
from app.models.predict_response import PredictResponse
from app.services.prediction_service import executar_previsao

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    """
    Recebe histórico de vendas de um produto e retorna previsão de demanda,
    KPIs de estoque e métricas comparativas dos modelos Holt-Winters e Prophet.
    """
    try:
        return executar_previsao(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("[produto_id=%d] Falha no motor: %s", request.produto_id, exc)
        raise HTTPException(status_code=500, detail="Erro interno no motor preditivo") from exc
    except Exception as exc:
        logger.error("[produto_id=%d] Erro inesperado: %s", request.produto_id, exc)
        raise HTTPException(status_code=500, detail="Erro interno no motor preditivo") from exc
