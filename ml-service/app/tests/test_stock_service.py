"""
Testes matemáticos do stock_service.

Cada caso de teste usa valores escolhidos para produzir resultados exatos
ou verificáveis analiticamente, garantindo que as fórmulas de Ballou (2006)
estão implementadas corretamente.
"""
import math

import pytest
from scipy import stats

from app.services.stock_service import (
    calcular_dias_ate_ruptura,
    calcular_estoque_seguranca,
    calcular_ponto_reposicao,
    calcular_z_score,
)


class TestCalcularZScore:
    def test_nivel_servico_50_retorna_zero(self):
        """Nível de serviço 50 % → Z = 0 (mediana da normal padrão)."""
        assert calcular_z_score(0.50) == pytest.approx(0.0, abs=1e-9)

    def test_nivel_servico_95(self):
        """Nível de serviço 95 % → Z ≈ 1.6449 (valor de referência da literatura)."""
        esperado = stats.norm.ppf(0.95)
        assert calcular_z_score(0.95) == pytest.approx(esperado, rel=1e-6)

    def test_nivel_servico_99(self):
        """Nível de serviço 99 % → Z ≈ 2.3263."""
        esperado = stats.norm.ppf(0.99)
        assert calcular_z_score(0.99) == pytest.approx(esperado, rel=1e-6)

    def test_nivel_servico_90(self):
        """Nível de serviço 90 % → Z ≈ 1.2816."""
        esperado = stats.norm.ppf(0.90)
        assert calcular_z_score(0.90) == pytest.approx(esperado, rel=1e-6)

    def test_retorno_e_float(self):
        """Resultado deve ser do tipo float."""
        assert isinstance(calcular_z_score(0.95), float)


class TestCalcularEstoqueSeguranca:
    def test_caso_exato_sem_variabilidade_lead_time(self):
        """
        Com σ_LT = 0, a fórmula reduz a ES = Z × σ_d × √LT.

        Z=1, LT=9, σ_d=4, d=qualquer, σ_LT=0
        → ES = 1 × 4 × √9 = 1 × 4 × 3 = 12  (exato)
        """
        resultado = calcular_estoque_seguranca(
            z=1.0,
            lead_time_medio=9,
            desvio_demanda=4.0,
            demanda_media=10.0,
            variabilidade_lead_time=0.0,
        )
        assert resultado == pytest.approx(12.0, abs=1e-9)

    def test_caso_exato_sem_desvio_demanda(self):
        """
        Com σ_d = 0, a fórmula reduz a ES = Z × d × σ_LT.

        Z=2, LT=qualquer, σ_d=0, d=5, σ_LT=1
        → ES = 2 × 5 × 1 = 10  (exato)
        """
        resultado = calcular_estoque_seguranca(
            z=2.0,
            lead_time_medio=3,
            desvio_demanda=0.0,
            demanda_media=5.0,
            variabilidade_lead_time=1.0,
        )
        assert resultado == pytest.approx(10.0, abs=1e-9)

    def test_caso_combinado_resultado_exato(self):
        """
        Caso combinado com resultado analítico verificável.

        Z=1, LT=4, σ_d=3, d=0, σ_LT=2
        → radicando = 4×9 + 0×4 = 36
        → ES = 1 × √36 = 6  (exato)
        """
        resultado = calcular_estoque_seguranca(
            z=1.0,
            lead_time_medio=4,
            desvio_demanda=3.0,
            demanda_media=0.0,
            variabilidade_lead_time=2.0,
        )
        assert resultado == pytest.approx(6.0, abs=1e-9)

    def test_z_zero_retorna_estoque_zero(self):
        """Z = 0 (nível de serviço 50 %) → estoque de segurança = 0."""
        resultado = calcular_estoque_seguranca(
            z=0.0,
            lead_time_medio=3,
            desvio_demanda=5.0,
            demanda_media=10.0,
            variabilidade_lead_time=1.0,
        )
        assert resultado == pytest.approx(0.0, abs=1e-9)

    def test_resultado_nao_negativo(self):
        """Estoque de segurança nunca pode ser negativo."""
        resultado = calcular_estoque_seguranca(
            z=1.645,
            lead_time_medio=3,
            desvio_demanda=2.0,
            demanda_media=10.0,
            variabilidade_lead_time=1.0,
        )
        assert resultado >= 0.0

    def test_retorno_e_float(self):
        """Resultado deve ser do tipo float."""
        resultado = calcular_estoque_seguranca(1.0, 3, 2.0, 10.0, 1.0)
        assert isinstance(resultado, float)


class TestCalcularPontoReposicao:
    def test_caso_sem_estoque_seguranca(self):
        """Sem estoque de segurança: PR = demanda × lead_time."""
        resultado = calcular_ponto_reposicao(
            demanda_media=10.0,
            lead_time_medio=3,
            estoque_seguranca=0.0,
        )
        assert resultado == pytest.approx(30.0, abs=1e-9)

    def test_caso_com_estoque_seguranca(self):
        """PR = demanda × lead_time + estoque_segurança."""
        resultado = calcular_ponto_reposicao(
            demanda_media=10.0,
            lead_time_medio=3,
            estoque_seguranca=20.0,
        )
        assert resultado == pytest.approx(50.0, abs=1e-9)

    def test_lead_time_unitario(self):
        """Lead time de 1 dia: PR = demanda + ES."""
        resultado = calcular_ponto_reposicao(
            demanda_media=7.5,
            lead_time_medio=1,
            estoque_seguranca=2.5,
        )
        assert resultado == pytest.approx(10.0, abs=1e-9)

    def test_demanda_zero_retorna_estoque_seguranca(self):
        """Com demanda zero: PR equivale ao próprio estoque de segurança."""
        resultado = calcular_ponto_reposicao(
            demanda_media=0.0,
            lead_time_medio=5,
            estoque_seguranca=8.0,
        )
        assert resultado == pytest.approx(8.0, abs=1e-9)

    def test_retorno_e_float(self):
        """Resultado deve ser do tipo float."""
        resultado = calcular_ponto_reposicao(10.0, 3, 5.0)
        assert isinstance(resultado, float)


class TestCalcularDiasAteRuptura:
    def test_caso_simples(self):
        """40 unidades com demanda de 10/dia → 4 dias."""
        assert calcular_dias_ate_ruptura(40, 10.0) == pytest.approx(4.0, abs=1e-9)

    def test_divisao_nao_inteira(self):
        """100 unidades com demanda de 3.5/dia → ≈ 28.571 dias."""
        esperado = 100 / 3.5
        assert calcular_dias_ate_ruptura(100, 3.5) == pytest.approx(esperado, rel=1e-6)

    def test_estoque_zero_retorna_zero(self):
        """Estoque zerado com demanda positiva → 0 dias (já em ruptura)."""
        assert calcular_dias_ate_ruptura(0, 10.0) == pytest.approx(0.0, abs=1e-9)

    def test_demanda_zero_retorna_none(self):
        """Demanda zero → None (produto nunca vai faltar)."""
        assert calcular_dias_ate_ruptura(40, 0.0) is None

    def test_demanda_negativa_retorna_none(self):
        """Demanda negativa (dado inválido) → None, não divide por zero."""
        assert calcular_dias_ate_ruptura(40, -1.0) is None

    def test_demanda_muito_baixa(self):
        """Demanda quase zero não causa overflow — resultado é um float finito."""
        resultado = calcular_dias_ate_ruptura(10, 0.001)
        assert resultado is not None
        assert math.isfinite(resultado)
        assert resultado == pytest.approx(10_000.0, rel=1e-6)

    def test_retorno_e_float_quando_demanda_positiva(self):
        """Resultado deve ser float quando demanda > 0."""
        resultado = calcular_dias_ate_ruptura(50, 5.0)
        assert isinstance(resultado, float)
