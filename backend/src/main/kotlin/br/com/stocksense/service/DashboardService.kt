package br.com.stocksense.service

import br.com.stocksense.dto.response.DashboardResponse
import br.com.stocksense.dto.response.SemanaFaturamentoResponse
import br.com.stocksense.repository.FaturamentoDiarioProjecao
import br.com.stocksense.repository.MetricaModeloRepository
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.DayOfWeek
import java.time.LocalDate
import java.time.temporal.TemporalAdjusters

/**
 * KPIs do dashboard (Tela 2): contagens de risco/crítico por dias até ruptura,
 * MAPE médio do modelo selecionado (nunca fixo num modelo só) e série de
 * faturamento semanal dos últimos 2 meses.
 */
@Service
class DashboardService(
    private val produtoRepository: ProdutoRepository,
    private val metricaModeloRepository: MetricaModeloRepository,
    private val vendaRepository: VendaRepository,
) {

    private companion object {
        val LIMITE_RISCO_DIAS = BigDecimal(7)
        val LIMITE_CRITICO_DIAS = BigDecimal(3)
        const val SEMANAS_HISTORICO = 8L
        const val ESCALA_MAPE = 4
    }

    @Transactional(readOnly = true)
    fun resumo(estabelecimentoId: Int): DashboardResponse {
        val inicio = LocalDate.now()
            .minusWeeks(SEMANAS_HISTORICO)
            .with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY))

        return DashboardResponse(
            riscoDeFaltar7Dias = produtoRepository
                .countByEstabelecimentoIdAndDiasAteRupturaLessThanEqual(estabelecimentoId, LIMITE_RISCO_DIAS),
            criticoAgora = produtoRepository
                .countByEstabelecimentoIdAndDiasAteRupturaLessThan(estabelecimentoId, LIMITE_CRITICO_DIAS),
            mapeMedioModeloSelecionado = metricaModeloRepository.mapeMedioSelecionado(estabelecimentoId)
                ?.let { BigDecimal.valueOf(it).setScale(ESCALA_MAPE, RoundingMode.HALF_UP) },
            seriesFaturamento = agruparPorSemana(
                vendaRepository.agregarFaturamentoDiario(estabelecimentoId, inicio.atStartOfDay()),
            ),
        )
    }

    /**
     * Agrupa os totais diários por semana (chave = segunda-feira). Dias sem
     * `valor_venda` (total nulo) contribuem com zero. Semanas sem nenhuma venda
     * não aparecem na série.
     */
    private fun agruparPorSemana(dias: List<FaturamentoDiarioProjecao>): List<SemanaFaturamentoResponse> =
        dias.groupBy { it.data.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY)) }
            .map { (semana, itens) ->
                SemanaFaturamentoResponse(
                    semana = semana,
                    total = itens.fold(BigDecimal.ZERO) { acc, d -> acc + (d.total ?: BigDecimal.ZERO) },
                )
            }
            .sortedBy { it.semana }
}