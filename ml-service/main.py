from fastapi import FastAPI

app = FastAPI(
    title="Motor Preditivo de Estoque — AI/ML Service",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Verifica se o serviço está operacional."""
    return {"status": "ok"}
