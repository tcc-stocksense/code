"""
Testes do abc_service.

Valida matematicamente os limites exatos da classificação A/B/C
(79.9 %, 80.0 %, 80.1 %, 94.9 %, 95.0 %, 95.1 %) e o comportamento
da classificação completa de uma lista de produtos.
"""
import logging

import pytest

from app.services.abc_service import ResultadoAbc, _atribuir_classe, classificar_abc


class TestAtribuirClasse:
    """Valida os limites exatos das faixas A, B e C."""

    def test_limite_inferior_classe_a(self):
        """0.0 % acumulado — início absoluto da classe A."""
        assert _atribuir_classe(0.0) == "A"

    def test_abaixo_limiar_a(self):
        """79.9 % — ainda dentro de A."""
        assert _atribuir_classe(79.9) == "A"

    def test_exatamente_limiar_a(self):
        """80.0 % — exatamente no limite: deve ser A (≤ 80)."""
        assert _atribuir_classe(80.0) == "A"

    def test_acima_limiar_a(self):
        """80.1 % — primeiro ponto de B."""
        assert _atribuir_classe(80.1) == "B"

    def test_abaixo_limiar_b(self):
        """94.9 % — ainda dentro de B."""
        assert _atribuir_classe(94.9) == "B"

    def test_exatamente_limiar_b(self):
        """95.0 % — exatamente no limite: deve ser B (≤ 95)."""
        assert _atribuir_classe(95.0) == "B"

    def test_acima_limiar_b(self):
        """95.1 % — primeiro ponto de C."""
        assert _atribuir_classe(95.1) == "C"

    def test_limite_superior_classe_c(self):
        """100.0 % — último produto sempre é C."""
        assert _atribuir_classe(100.0) == "C"


class TestClassificarAbc:
    """Integração: classificação de uma lista de produtos."""

    def _make_dado(self, produto_id: int, faturamento: float | None, quantidade: int = 0) -> dict:
        return {"produto_id": produto_id, "faturamento": faturamento, "quantidade": quantidade}

    def test_caso_padrao_atinge_limiares_exatos(self):
        """
        Produtos com faturamento [800, 150, 50] sobre total 1000:
            P1 → 80.0 %  → A
            P2 → 95.0 %  → B
            P3 → 100.0 % → C
        Esse dataset foi escolhido por produzir exatamente os limiares.
        """
        dados = [
            self._make_dado(1, 800.0),
            self._make_dado(2, 150.0),
            self._make_dado(3,  50.0),
        ]
        resultados, abc_proxy = classificar_abc(dados)

        assert abc_proxy is False
        assert len(resultados) == 3

        por_id = {r.produto_id: r for r in resultados}
        assert por_id[1].classe == "A"
        assert por_id[1].percentual_acumulado == pytest.approx(80.0, abs=1e-4)
        assert por_id[2].classe == "B"
        assert por_id[2].percentual_acumulado == pytest.approx(95.0, abs=1e-4)
        assert por_id[3].classe == "C"
        assert por_id[3].percentual_acumulado == pytest.approx(100.0, abs=1e-4)

    def test_produto_unico_sempre_classe_a(self):
        """Um único produto representa 100 % do faturamento — começa em A."""
        dados = [self._make_dado(1, 500.0)]
        resultados, _ = classificar_abc(dados)

        assert len(resultados) == 1
        assert resultados[0].classe == "A"
        assert resultados[0].percentual_acumulado == pytest.approx(100.0, abs=1e-4)

    def test_ordenacao_decrescente_por_faturamento(self):
        """Resultados devem estar ordenados por faturamento decrescente."""
        dados = [
            self._make_dado(1,  50.0),
            self._make_dado(2, 800.0),
            self._make_dado(3, 150.0),
        ]
        resultados, _ = classificar_abc(dados)

        assert resultados[0].produto_id == 2   # maior faturamento primeiro
        assert resultados[1].produto_id == 3
        assert resultados[2].produto_id == 1

    def test_desempate_por_produto_id_ascendente(self):
        """Produtos com faturamento igual são ordenados por produto_id crescente."""
        dados = [
            self._make_dado(3, 100.0),
            self._make_dado(1, 100.0),
            self._make_dado(2, 100.0),
        ]
        resultados, _ = classificar_abc(dados)

        ids_ordenados = [r.produto_id for r in resultados]
        assert ids_ordenados == [1, 2, 3]

    def test_proxy_quando_faturamento_ausente(self):
        """faturamento=None ativa abc_proxy e usa quantidade."""
        dados = [
            {"produto_id": 1, "faturamento": None, "quantidade": 80},
            {"produto_id": 2, "faturamento": None, "quantidade": 20},
        ]
        resultados, abc_proxy = classificar_abc(dados)

        assert abc_proxy is True
        por_id = {r.produto_id: r for r in resultados}
        assert por_id[1].classe == "A"   # 80 % acumulado
        assert por_id[2].classe == "C"   # 100 % acumulado

    def test_proxy_emite_aviso_no_log(self, caplog):
        """Fallback por proxy deve registrar WARNING no log."""
        dados = [{"produto_id": 1, "faturamento": None, "quantidade": 10}]
        with caplog.at_level(logging.WARNING, logger="app.services.abc_service"):
            classificar_abc(dados)

        assert "proxy" in caplog.text.lower()

    def test_proxy_quando_faturamento_zerado(self):
        """Faturamento total = 0 também aciona proxy."""
        dados = [
            {"produto_id": 1, "faturamento": 0.0, "quantidade": 50},
            {"produto_id": 2, "faturamento": 0.0, "quantidade": 50},
        ]
        _, abc_proxy = classificar_abc(dados)
        assert abc_proxy is True

    def test_lista_vazia_retorna_listas_vazias(self):
        """Lista de entrada vazia deve retornar resultado vazio sem erro."""
        resultados, abc_proxy = classificar_abc([])

        assert resultados == []
        assert abc_proxy is False

    def test_todos_valores_zerados_retorna_classe_c(self):
        """Quando nenhuma métrica tem valor > 0, todos recebem classe C."""
        dados = [
            {"produto_id": 1, "faturamento": 0.0, "quantidade": 0},
            {"produto_id": 2, "faturamento": 0.0, "quantidade": 0},
        ]
        resultados, _ = classificar_abc(dados)

        assert all(r.classe == "C" for r in resultados)

    def test_resultado_e_dataclass_imutavel(self):
        """ResultadoAbc é frozen — não deve permitir atribuição de atributo."""
        dados = [self._make_dado(1, 100.0)]
        resultados, _ = classificar_abc(dados)

        with pytest.raises((AttributeError, TypeError)):
            resultados[0].classe = "X"  # type: ignore[misc]
