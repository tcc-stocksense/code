"""
Testes do holt_winters_service.

Cobre: série normal, fallback por série curta, zeros excessivos,
série inválida, integridade do índice temporal e finitude das métricas.
"""
import logging

import numpy as np
import pandas as pd
import pytest

from app.models.predict_response import MetricasModelo
from app.services.holt_winters_service import treinar_e_avaliar


class TestSerieNormal:
    def test_retorna_metricas_e_previsao(self, serie_90_dias):
        """Série válida de 90 dias deve retornar métricas e previsão completas."""
        metricas, previsao = treinar_e_avaliar(serie_90_dias)

        assert isinstance(metricas, MetricasModelo)
        assert len(previsao) == 30

    def test_metricas_sao_nao_negativas(self, serie_90_dias):
        """MAPE, RMSE e MAE não podem ser negativos."""
        metricas, _ = treinar_e_avaliar(serie_90_dias)

        assert metricas.mape >= 0
        assert metricas.rmse >= 0
        assert metricas.mae >= 0

    def test_metricas_sao_finitas(self, serie_90_dias):
        """Métricas não podem ser NaN ou infinito."""
        metricas, _ = treinar_e_avaliar(serie_90_dias)

        assert np.isfinite(metricas.mape)
        assert np.isfinite(metricas.rmse)
        assert np.isfinite(metricas.mae)

    def test_previsao_sem_valores_negativos(self, serie_90_dias):
        """Quantidade prevista não pode ser negativa."""
        _, previsao = treinar_e_avaliar(serie_90_dias)

        assert (previsao >= 0).all()

    def test_previsao_continua_apos_ultimo_dia_da_serie(self, serie_90_dias):
        """O primeiro dia da previsão deve ser posterior ao último da série."""
        _, previsao = treinar_e_avaliar(serie_90_dias)

        assert previsao.index[0] > serie_90_dias.index[-1]


class TestFallbackSerieCurta:
    def test_serie_curta_nao_levanta_excecao(self, serie_curta):
        """Série com menos de 14 dias deve processar sem erro via fallback."""
        metricas, previsao = treinar_e_avaliar(serie_curta)

        assert isinstance(metricas, MetricasModelo)
        assert len(previsao) == 30

    def test_serie_curta_emite_aviso_de_sazonalidade(self, serie_curta, caplog):
        """Série abaixo de 14 dias deve registrar aviso sobre sazonalidade."""
        with caplog.at_level(logging.WARNING, logger="app.services.holt_winters_service"):
            treinar_e_avaliar(serie_curta)

        assert "sazonalidade" in caplog.text.lower()

    def test_previsao_serie_curta_sem_valores_negativos(self, serie_curta):
        """Previsão via fallback não pode conter valores negativos."""
        _, previsao = treinar_e_avaliar(serie_curta)

        assert (previsao >= 0).all()


class TestZerosExcessivos:
    def test_zeros_excessivos_nao_levanta_excecao(self, serie_com_zeros_excessivos):
        """Série com > 30 % de zeros deve processar e retornar resultado válido."""
        metricas, previsao = treinar_e_avaliar(serie_com_zeros_excessivos)

        assert isinstance(metricas, MetricasModelo)
        assert len(previsao) == 30

    def test_zeros_excessivos_emite_aviso(self, serie_com_zeros_excessivos, caplog):
        """Série com > 30 % de zeros deve registrar aviso no log."""
        with caplog.at_level(logging.WARNING, logger="app.services.holt_winters_service"):
            treinar_e_avaliar(serie_com_zeros_excessivos)

        assert "zeros" in caplog.text.lower()

    def test_mape_calculado_apenas_sobre_nao_zeros(self, serie_com_zeros_excessivos):
        """MAPE deve ser finito mesmo com muitos zeros — não divide por zero."""
        metricas, _ = treinar_e_avaliar(serie_com_zeros_excessivos)

        assert np.isfinite(metricas.mape)


class TestSerieInvalida:
    def test_serie_muito_curta_levanta_value_error(self):
        """Série com menos de 10 observações não-nulas deve levantar ValueError."""
        serie = pd.Series(
            [5.0, 3.0, 0.0, 7.0, 0.0],
            index=pd.date_range("2024-01-01", periods=5),
        )
        with pytest.raises(ValueError, match="insuficiente"):
            treinar_e_avaliar(serie)

    def test_serie_toda_zeros_levanta_value_error(self):
        """Série com todos os valores zero deve levantar ValueError."""
        serie = pd.Series(
            [0.0] * 30,
            index=pd.date_range("2024-01-01", periods=30),
        )
        with pytest.raises(ValueError, match="insuficiente"):
            treinar_e_avaliar(serie)
