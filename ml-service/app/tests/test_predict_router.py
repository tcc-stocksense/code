"""
Testes do endpoint POST /predict e GET /health.

Usa TestClient (síncrono) com mock de executar_previsao para testar
o comportamento HTTP do router sem acionar os modelos de ML — mantendo
os testes rápidos e focados na camada de roteamento.
"""
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.models.predict_response import MetricasModelo, PrevisaoDiaria, PredictResponse
from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Cliente HTTP síncrono apontando para a aplicação FastAPI."""
    return TestClient(app)


def _resposta_mock(produto_id: int = 1) -> PredictResponse:
    """Constrói uma PredictResponse mínima e válida para uso nos mocks."""
    metricas_hw = MetricasModelo(mape=8.2, rmse=2.1, mae=1.8)
    metricas_pr = MetricasModelo(mape=10.5, rmse=2.7, mae=2.3)
    previsoes = [
        PrevisaoDiaria(data=date(2024, 4, min(i + 1, 30)), quantidade_prevista=12.0)
        for i in range(30)
    ]
    return PredictResponse(
        produto_id=produto_id,
        modelo_selecionado="holt_winters",
        previsoes=previsoes,
        metricas={"holt_winters": metricas_hw, "prophet": metricas_pr},
        ponto_reposicao=52.0,
        estoque_seguranca=10.0,
        dias_ate_ruptura=18.0,
        classe_abc="C",
        abc_proxy=True,
        aviso=None,
    )


class TestGetHealth:
    def test_retorna_200(self, client: TestClient):
        """GET /health deve retornar 200 OK."""
        assert client.get("/health").status_code == 200

    def test_corpo_contem_status_ok(self, client: TestClient):
        """Corpo da resposta deve conter status='ok'."""
        dados = client.get("/health").json()
        assert dados["status"] == "ok"

    def test_corpo_contem_nome_servico(self, client: TestClient):
        """Resposta deve identificar o serviço como 'ml-service'."""
        dados = client.get("/health").json()
        assert dados.get("service") == "ml-service"


class TestPostPredictValidacao:
    """Testes de validação de payload — nenhum mock necessário."""

    def test_historico_abaixo_de_90_dias_retorna_422(
        self, client: TestClient, payload_valido: dict
    ):
        """Pydantic rejeita historico com menos de 90 entradas → 422."""
        payload = {**payload_valido, "historico": payload_valido["historico"][:50]}
        assert client.post("/predict", json=payload).status_code == 422

    def test_produto_id_nao_inteiro_retorna_422(
        self, client: TestClient, payload_valido: dict
    ):
        """produto_id deve ser inteiro — string inválida gera 422."""
        payload = {**payload_valido, "produto_id": "abc"}
        assert client.post("/predict", json=payload).status_code == 422

    def test_nivel_servico_acima_do_limite_retorna_422(
        self, client: TestClient, payload_valido: dict
    ):
        """nivel_servico_alvo > 0.999 viola a regra Field(le=0.999) → 422."""
        payload = {**payload_valido, "nivel_servico_alvo": 1.5}
        assert client.post("/predict", json=payload).status_code == 422

    def test_nivel_servico_abaixo_do_limite_retorna_422(
        self, client: TestClient, payload_valido: dict
    ):
        """nivel_servico_alvo < 0.5 viola a regra Field(ge=0.5) → 422."""
        payload = {**payload_valido, "nivel_servico_alvo": 0.1}
        assert client.post("/predict", json=payload).status_code == 422

    def test_estoque_atual_negativo_retorna_422(
        self, client: TestClient, payload_valido: dict
    ):
        """estoque_atual negativo viola Field(ge=0) → 422."""
        payload = {**payload_valido, "estoque_atual": -1}
        assert client.post("/predict", json=payload).status_code == 422

    def test_lead_time_zero_retorna_422(
        self, client: TestClient, payload_valido: dict
    ):
        """lead_time_medio=0 viola Field(ge=1) → 422."""
        payload = {**payload_valido, "lead_time_medio": 0}
        assert client.post("/predict", json=payload).status_code == 422


class TestPostPredictSucesso:
    """Testes do caminho feliz com mock de executar_previsao."""

    def test_payload_valido_retorna_200(
        self, client: TestClient, payload_valido: dict
    ):
        """Payload válido com serviço mockado deve retornar 200."""
        with patch(
            "app.routers.predict_router.executar_previsao",
            new_callable=AsyncMock,
            return_value=_resposta_mock(),
        ):
            response = client.post("/predict", json=payload_valido)
        assert response.status_code == 200

    def test_resposta_contem_produto_id(
        self, client: TestClient, payload_valido: dict
    ):
        """produto_id da resposta deve corresponder ao do request."""
        with patch(
            "app.routers.predict_router.executar_previsao",
            new_callable=AsyncMock,
            return_value=_resposta_mock(produto_id=1),
        ):
            dados = client.post("/predict", json=payload_valido).json()
        assert dados["produto_id"] == 1

    def test_resposta_contem_campos_obrigatorios(
        self, client: TestClient, payload_valido: dict
    ):
        """Resposta deve incluir todos os campos definidos em PredictResponse."""
        campos_esperados = {
            "produto_id", "modelo_selecionado", "previsoes", "metricas",
            "ponto_reposicao", "estoque_seguranca", "dias_ate_ruptura",
            "classe_abc", "abc_proxy",
        }
        with patch(
            "app.routers.predict_router.executar_previsao",
            new_callable=AsyncMock,
            return_value=_resposta_mock(),
        ):
            dados = client.post("/predict", json=payload_valido).json()
        assert campos_esperados.issubset(dados.keys())

    def test_previsoes_tem_30_entradas(
        self, client: TestClient, payload_valido: dict
    ):
        """Lista de previsões deve conter exatamente 30 dias."""
        with patch(
            "app.routers.predict_router.executar_previsao",
            new_callable=AsyncMock,
            return_value=_resposta_mock(),
        ):
            dados = client.post("/predict", json=payload_valido).json()
        assert len(dados["previsoes"]) == 30

    def test_modelo_selecionado_e_string_valida(
        self, client: TestClient, payload_valido: dict
    ):
        """modelo_selecionado deve ser 'holt_winters' ou 'prophet'."""
        with patch(
            "app.routers.predict_router.executar_previsao",
            new_callable=AsyncMock,
            return_value=_resposta_mock(),
        ):
            dados = client.post("/predict", json=payload_valido).json()
        assert dados["modelo_selecionado"] in {"holt_winters", "prophet"}


class TestPostPredictErros:
    """Testes de tratamento de erros no router."""

    def test_runtime_error_retorna_500(
        self, client: TestClient, payload_valido: dict
    ):
        """RuntimeError no serviço deve gerar HTTP 500."""
        with patch(
            "app.routers.predict_router.executar_previsao",
            new_callable=AsyncMock,
            side_effect=RuntimeError("ambos os modelos falharam"),
        ):
            response = client.post("/predict", json=payload_valido)
        assert response.status_code == 500

    def test_stack_trace_nao_vaza_para_o_cliente(
        self, client: TestClient, payload_valido: dict
    ):
        """Stack trace Python nunca deve aparecer na resposta ao cliente."""
        with patch(
            "app.routers.predict_router.executar_previsao",
            new_callable=AsyncMock,
            side_effect=RuntimeError("falha interna"),
        ):
            response = client.post("/predict", json=payload_valido)
        assert "RuntimeError" not in response.text
        assert "Traceback" not in response.text

    def test_mensagem_de_erro_e_generica(
        self, client: TestClient, payload_valido: dict
    ):
        """Mensagem de erro 500 deve ser genérica, sem detalhes internos."""
        with patch(
            "app.routers.predict_router.executar_previsao",
            new_callable=AsyncMock,
            side_effect=RuntimeError("detalhe interno sensível"),
        ):
            body = client.post("/predict", json=payload_valido).json()
        assert "detalhe interno sensível" not in str(body)
        assert body.get("detail") == "Erro interno no motor preditivo"
