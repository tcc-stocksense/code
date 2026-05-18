from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """Verifica se o serviço está operacional."""
    return {"status": "ok", "service": "ml-service", "version": "1.0.0"}
