package br.com.stocksense.service

import br.com.stocksense.domain.MetricaModelo
import br.com.stocksense.domain.Produto
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.MetricaModeloRepository
import br.com.stocksense.repository.ProdutoRepository
import io.mockk.every
import io.mockk.mockk
import java.math.BigDecimal
import java.time.LocalDateTime
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class MetricaServiceTest {

    private val produtoRepository = mockk<ProdutoRepository>()
    private val metricaModeloRepository = mockk<MetricaModeloRepository>()
    private lateinit var metricaService: MetricaService

    @BeforeTest
    fun setUp() {
        metricaService = MetricaService(produtoRepository, metricaModeloRepository)
    }

    private fun metrica(modelo: String, mape: String, selecionado: Boolean): MetricaModelo =
        MetricaModelo(
            produtoId = 1,
            modelo = modelo,
            mape = BigDecimal(mape),
            rmse = BigDecimal("2.0"),
            mae = BigDecimal("1.5"),
            selecionado = selecionado,
            executadoEm = LocalDateTime.of(2025, 4, 1, 3, 0),
        )

    @Test
    fun `metricas retorna as duas linhas mais recentes com o vencedor primeiro`() {
        val produto = Produto(produtoId = 1, estabelecimentoId = 1, nome = "Arroz", estoqueAtual = 40)
        every { produtoRepository.findByProdutoId(1) } returns produto
        every { metricaModeloRepository.findMetricasMaisRecentes(1) } returns listOf(
            metrica("prophet", "12.0", selecionado = false),
            metrica("holt_winters", "8.0", selecionado = true),
        )

        val response = metricaService.metricas(estabelecimentoId = 1, produtoId = 1)

        assertEquals(2, response.size)
        assertEquals("holt_winters", response.first().modelo)
        assertTrue(response.first().selecionado)
    }

    @Test
    fun `metricas sem execucao do motor retorna lista vazia`() {
        val produto = Produto(produtoId = 1, estabelecimentoId = 1, nome = "Arroz", estoqueAtual = 40)
        every { produtoRepository.findByProdutoId(1) } returns produto
        every { metricaModeloRepository.findMetricasMaisRecentes(1) } returns emptyList()

        assertTrue(metricaService.metricas(estabelecimentoId = 1, produtoId = 1).isEmpty())
    }

    @Test
    fun `metricas de produto inexistente lanca RecursoNaoEncontradoException`() {
        every { produtoRepository.findByProdutoId(99) } returns null

        assertFailsWith<RecursoNaoEncontradoException> {
            metricaService.metricas(estabelecimentoId = 1, produtoId = 99)
        }
    }

    @Test
    fun `metricas de produto de outro estabelecimento lanca RecursoNaoEncontradoException`() {
        val produto = Produto(produtoId = 5, estabelecimentoId = 2, nome = "Açúcar", estoqueAtual = 15)
        every { produtoRepository.findByProdutoId(5) } returns produto

        assertFailsWith<RecursoNaoEncontradoException> {
            metricaService.metricas(estabelecimentoId = 1, produtoId = 5)
        }
    }
}