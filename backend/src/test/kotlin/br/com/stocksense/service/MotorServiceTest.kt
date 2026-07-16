package br.com.stocksense.service

import br.com.stocksense.client.MlServiceClient
import br.com.stocksense.client.dto.MetricasModelo
import br.com.stocksense.client.dto.PredictResponse
import br.com.stocksense.client.dto.PrevisaoDiaria
import br.com.stocksense.domain.MetricaModelo
import br.com.stocksense.domain.Previsao
import br.com.stocksense.domain.Produto
import br.com.stocksense.exception.MotorPreditivoException
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.MetricaModeloRepository
import br.com.stocksense.repository.PrevisaoRepository
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaDiariaProjecao
import br.com.stocksense.repository.VendaRepository
import feign.FeignException
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import java.math.BigDecimal
import java.time.LocalDate
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

/** FeignException concreta para simular indisponibilidade do ml-service sem mock. */
private class FakeFeignException : FeignException(503, "ml-service indisponível")

class MotorServiceTest {

    private val produtoRepository = mockk<ProdutoRepository>()
    private val vendaRepository = mockk<VendaRepository>()
    private val previsaoRepository = mockk<PrevisaoRepository>(relaxed = true)
    private val metricaRepository = mockk<MetricaModeloRepository>(relaxed = true)
    private val mlServiceClient = mockk<MlServiceClient>()
    private lateinit var motorService: MotorService

    @BeforeTest
    fun setUp() {
        motorService = MotorService(
            produtoRepository, vendaRepository, previsaoRepository, metricaRepository, mlServiceClient,
        )
    }

    private fun vendaDia(dia: LocalDate, total: Long): VendaDiariaProjecao =
        object : VendaDiariaProjecao {
            override val data = dia
            override val total = total
        }

    @Test
    fun `executarMotor persiste previsoes, metricas e atualiza o produto`() {
        val produto = Produto(produtoId = 1, nome = "Arroz", estoqueAtual = 40)
        every { produtoRepository.findByProdutoId(1) } returns produto
        every { vendaRepository.agregarVendasDiarias(1) } returns listOf(
            vendaDia(LocalDate.of(2025, 1, 1), 10),
            vendaDia(LocalDate.of(2025, 1, 2), 12),
        )
        every { produtoRepository.save(any()) } answers { firstArg() }

        val resposta = PredictResponse(
            produtoId = 1,
            modeloSelecionado = "holt_winters",
            previsoes = listOf(
                PrevisaoDiaria(LocalDate.of(2025, 4, 1), BigDecimal("11.5")),
                PrevisaoDiaria(LocalDate.of(2025, 4, 2), BigDecimal("12.0")),
            ),
            metricas = mapOf(
                "holt_winters" to MetricasModelo(BigDecimal("8.0"), BigDecimal("2.0"), BigDecimal("1.5")),
                "prophet" to MetricasModelo(BigDecimal("12.0"), BigDecimal("3.0"), BigDecimal("2.5")),
            ),
            pontoReposicao = BigDecimal("55.00"),
            estoqueSeguranca = BigDecimal("15.00"),
            diasAteRuptura = BigDecimal("3.48"),
            desvioPadraoDemanda = BigDecimal("2.2561"),
        )
        every { mlServiceClient.predict(any()) } returns resposta

        val previsoesSalvas = slot<List<Previsao>>()
        val metricasSalvas = slot<List<MetricaModelo>>()
        every { previsaoRepository.saveAll(capture(previsoesSalvas)) } answers { firstArg() }
        every { metricaRepository.saveAll(capture(metricasSalvas)) } answers { firstArg() }

        motorService.executarMotor(1)

        // 2 previsões, todas com o modelo vencedor e mesmo executadoEm
        assertEquals(2, previsoesSalvas.captured.size)
        assertTrue(previsoesSalvas.captured.all { it.modeloUtilizado == "holt_winters" })
        assertEquals(1, previsoesSalvas.captured.map { it.executadoEm }.toSet().size)
        assertEquals(BigDecimal("11.5"), previsoesSalvas.captured[0].quantidadePrevista)

        // 2 métricas, flag selecionado apenas no modelo vencedor
        assertEquals(2, metricasSalvas.captured.size)
        assertEquals(true, metricasSalvas.captured.first { it.modelo == "holt_winters" }.selecionado)
        assertEquals(false, metricasSalvas.captured.first { it.modelo == "prophet" }.selecionado)

        // Produto atualizado com os KPIs do motor
        assertEquals(BigDecimal("55.00"), produto.pontoReposicao)
        assertEquals(BigDecimal("15.00"), produto.estoqueSeguranca)
        assertEquals(BigDecimal("2.2561"), produto.desvioPadraoDemanda)
        assertEquals(BigDecimal("3.48"), produto.diasAteRuptura)
        assertNotNull(produto.dataUltimoCalculo)
        verify { produtoRepository.save(produto) }
    }

    @Test
    fun `executarMotor converte falha do ml-service em MotorPreditivoException`() {
        val produto = Produto(produtoId = 2, nome = "Feijão", estoqueAtual = 20)
        every { produtoRepository.findByProdutoId(2) } returns produto
        every { vendaRepository.agregarVendasDiarias(2) } returns listOf(vendaDia(LocalDate.of(2025, 1, 1), 5))
        every { mlServiceClient.predict(any()) } throws FakeFeignException()

        assertFailsWith<MotorPreditivoException> {
            motorService.executarMotor(2)
        }
    }

    @Test
    fun `executarMotor lanca RecursoNaoEncontradoException quando produto nao existe`() {
        every { produtoRepository.findByProdutoId(99) } returns null

        assertFailsWith<RecursoNaoEncontradoException> {
            motorService.executarMotor(99)
        }
    }
}
