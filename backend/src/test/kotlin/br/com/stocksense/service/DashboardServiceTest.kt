package br.com.stocksense.service

import br.com.stocksense.repository.FaturamentoDiarioProjecao
import br.com.stocksense.repository.MetricaModeloRepository
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaRepository
import io.mockk.every
import io.mockk.mockk
import java.math.BigDecimal
import java.time.LocalDate
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

class DashboardServiceTest {

    private val produtoRepository = mockk<ProdutoRepository>()
    private val metricaModeloRepository = mockk<MetricaModeloRepository>()
    private val vendaRepository = mockk<VendaRepository>()
    private lateinit var dashboardService: DashboardService

    @BeforeTest
    fun setUp() {
        dashboardService = DashboardService(produtoRepository, metricaModeloRepository, vendaRepository)
        // Defaults neutros; cada teste sobrescreve o que interessa
        every {
            produtoRepository.countByEstabelecimentoIdAndDiasAteRupturaLessThanEqual(1, BigDecimal(7))
        } returns 0
        every {
            produtoRepository.countByEstabelecimentoIdAndDiasAteRupturaLessThan(1, BigDecimal(3))
        } returns 0
        every { metricaModeloRepository.mapeMedioSelecionado(1) } returns null
        every { vendaRepository.agregarFaturamentoDiario(1, any()) } returns emptyList()
    }

    private fun dia(data: LocalDate, total: String?): FaturamentoDiarioProjecao =
        object : FaturamentoDiarioProjecao {
            override val data = data
            override val total = total?.let { BigDecimal(it) }
        }

    @Test
    fun `contagens de risco e critico vem das queries por dias ate ruptura`() {
        every {
            produtoRepository.countByEstabelecimentoIdAndDiasAteRupturaLessThanEqual(1, BigDecimal(7))
        } returns 7
        every {
            produtoRepository.countByEstabelecimentoIdAndDiasAteRupturaLessThan(1, BigDecimal(3))
        } returns 3

        val resumo = dashboardService.resumo(1)

        assertEquals(7, resumo.riscoDeFaltar7Dias)
        assertEquals(3, resumo.criticoAgora)
    }

    @Test
    fun `mape medio e arredondado em 4 casas`() {
        every { metricaModeloRepository.mapeMedioSelecionado(1) } returns 12.345678

        val resumo = dashboardService.resumo(1)

        assertEquals(BigDecimal("12.3457"), resumo.mapeMedioModeloSelecionado)
    }

    @Test
    fun `mape medio nulo quando o motor nunca rodou`() {
        val resumo = dashboardService.resumo(1)

        assertNull(resumo.mapeMedioModeloSelecionado)
    }

    @Test
    fun `serie agrupa totais diarios por semana iniciada na segunda`() {
        // 2025-01-06 é segunda; 2025-01-08 mesma semana; 2025-01-13 semana seguinte
        every { vendaRepository.agregarFaturamentoDiario(1, any()) } returns listOf(
            dia(LocalDate.of(2025, 1, 6), "100.00"),
            dia(LocalDate.of(2025, 1, 8), "50.00"),
            dia(LocalDate.of(2025, 1, 13), "80.00"),
        )

        val serie = dashboardService.resumo(1).seriesFaturamento

        assertEquals(2, serie.size)
        assertEquals(LocalDate.of(2025, 1, 6), serie[0].semana)
        assertEquals(BigDecimal("150.00"), serie[0].total)
        assertEquals(LocalDate.of(2025, 1, 13), serie[1].semana)
        assertEquals(BigDecimal("80.00"), serie[1].total)
    }

    @Test
    fun `dia sem valor_venda contribui com zero na semana`() {
        every { vendaRepository.agregarFaturamentoDiario(1, any()) } returns listOf(
            dia(LocalDate.of(2025, 1, 6), "100.00"),
            dia(LocalDate.of(2025, 1, 7), null),
        )

        val serie = dashboardService.resumo(1).seriesFaturamento

        assertEquals(BigDecimal("100.00"), serie.single().total)
    }

    @Test
    fun `sem vendas retorna serie vazia`() {
        assertTrue(dashboardService.resumo(1).seriesFaturamento.isEmpty())
    }
}