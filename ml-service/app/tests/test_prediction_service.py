"""
Testes da preparação da série no prediction_service.

Cobre: preenchimento dos dias sem venda com zero, ordenação, datas repetidas
e a equivalência com a série contínua usada no notebook de análise do TCC.
"""
from datetime import date, timedelta

import pandas as pd
import pytest

from app.models.predict_request import PredictRequest
from app.services import holt_winters_service
from app.services.prediction_service import _preparar_serie
from app.tests.generate_synthetic_data import gerar_dataset


def _request(historico: list[tuple[date, int]]) -> PredictRequest:
    """PredictRequest válido a partir de pares (data, quantidade)."""
    return PredictRequest(
        produto_id=1,
        historico=[{"data": d, "quantidade": q} for d, q in historico],
        estoque_atual=40,
    )


def _historico_com_buracos() -> list[tuple[date, int]]:
    """106 dias corridos (91 com venda) sem os domingos — como o backend envia uma loja fechada no domingo."""
    inicio = date(2024, 1, 1)  # segunda-feira
    dias = (inicio + timedelta(days=i) for i in range(106))
    return [(d, 10) for d in dias if d.weekday() != 6]


class TestDiasSemVenda:
    def test_indice_diario_continuo(self):
        """Os dias ausentes do payload voltam ao índice: nenhuma data pulada."""
        serie = _preparar_serie(_request(_historico_com_buracos()))

        esperado = pd.date_range("2024-01-01", periods=106, freq="D")
        assert serie.index.equals(esperado)
        assert serie.index.freq == "D"

    def test_dias_ausentes_valem_zero(self):
        """Domingos (fora do payload) entram com quantidade zero."""
        serie = _preparar_serie(_request(_historico_com_buracos()))

        domingos = serie[serie.index.dayofweek == 6]
        assert len(domingos) == 15
        assert (domingos == 0.0).all()
        assert (serie[serie.index.dayofweek != 6] == 10.0).all()

    def test_nao_estende_alem_do_historico(self):
        """O índice vai da primeira à última venda — sem zeros antes ou depois."""
        serie = _preparar_serie(_request(_historico_com_buracos()))

        assert serie.index[0] == pd.Timestamp("2024-01-01")
        assert serie.index[-1] == pd.Timestamp("2024-04-15")


class TestOrdemEDuplicatas:
    def test_ordena_cronologicamente(self):
        """Payload fora de ordem resulta em série ordenada."""
        historico = list(reversed(_historico_com_buracos()))
        serie = _preparar_serie(_request(historico))

        assert serie.index.is_monotonic_increasing

    def test_datas_repetidas_sao_somadas(self):
        """Duas linhas na mesma data viram um único dia com a soma."""
        historico = _historico_com_buracos() + [(date(2024, 1, 1), 5)]
        serie = _preparar_serie(_request(historico))

        assert serie.index.is_unique
        assert serie[pd.Timestamp("2024-01-01")] == 15.0


class TestEquivalenciaComAnalise:
    @pytest.mark.parametrize("produto_id", [2, 6, 8])
    def test_holt_winters_igual_ao_notebook(self, produto_id):
        """
        Regressão do desalinhamento de fase: a série montada só com os dias de
        venda (como o backend envia) deve produzir o mesmo MAPE do Holt-Winters
        que a série contínua do notebook (dataset sintético, seed 42).
        Sem o preenchimento, o MAPE desses produtos era de 3 a 5 vezes maior.
        """
        _, series = gerar_dataset()
        continua = series[produto_id].astype(float)
        enviada = [(ts.date(), int(q)) for ts, q in continua.items() if q > 0]

        serie = _preparar_serie(_request(enviada))
        metricas_sistema, _ = holt_winters_service.treinar_e_avaliar(serie)
        metricas_notebook, _ = holt_winters_service.treinar_e_avaliar(continua)

        assert metricas_sistema.mape == pytest.approx(metricas_notebook.mape, abs=0.5)
