package br.com.stocksense.service

import br.com.stocksense.domain.Produto
import br.com.stocksense.repository.ProdutoRepository
import io.mockk.every
import io.mockk.mockk
import java.math.BigDecimal
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class AlertaServiceTest {

    private val produtoRepository = mockk<ProdutoRepository>()
    private lateinit var alertaService: AlertaService

    @BeforeTest
    fun setUp() {
        alertaService = AlertaService(produtoRepository)
    }

    private fun produto(
        id: Int,
        nome: String,
        estoque: Int,
        pontoReposicao: String?,
        diasAteRuptura: String? = null,
    ): Produto = Produto(
        produtoId = id,
        estabelecimentoId = 1,
        nome = nome,
        estoqueAtual = estoque,
        pontoReposicao = pontoReposicao?.let { BigDecimal(it) },
        diasAteRuptura = diasAteRuptura?.let { BigDecimal(it) },
    )

    @Test
    fun `semaforo vermelho quando estoque menor ou igual ao ponto de reposicao`() {
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produto(1, "Arroz", estoque = 10, pontoReposicao = "10.00"),
        )

        val alertas = alertaService.listar(1)

        assertEquals(AlertaService.SEMAFORO_VERMELHO, alertas.single().semaforo)
    }

    @Test
    fun `semaforo amarelo quando estoque entre PR e PR vezes 1_5`() {
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produto(1, "Arroz", estoque = 15, pontoReposicao = "10.00"),
        )

        val alertas = alertaService.listar(1)

        assertEquals(AlertaService.SEMAFORO_AMARELO, alertas.single().semaforo)
    }

    @Test
    fun `semaforo verde quando estoque acima de PR vezes 1_5`() {
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produto(1, "Arroz", estoque = 16, pontoReposicao = "10.00"),
        )

        val alertas = alertaService.listar(1)

        assertEquals(AlertaService.SEMAFORO_VERDE, alertas.single().semaforo)
    }

    @Test
    fun `lista ordenada por urgencia com vermelhos primeiro e menor ruptura antes`() {
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produto(1, "Verde", estoque = 100, pontoReposicao = "10.00", diasAteRuptura = "30.00"),
            produto(2, "Vermelho lento", estoque = 5, pontoReposicao = "10.00", diasAteRuptura = "5.00"),
            produto(3, "Amarelo", estoque = 12, pontoReposicao = "10.00", diasAteRuptura = "9.00"),
            produto(4, "Vermelho urgente", estoque = 1, pontoReposicao = "10.00", diasAteRuptura = "1.00"),
        )

        val alertas = alertaService.listar(1)

        assertEquals(listOf(4, 2, 3, 1), alertas.map { it.produtoId })
    }

    @Test
    fun `produto sem ponto de reposicao fica fora da lista`() {
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produto(1, "Sem motor", estoque = 10, pontoReposicao = null),
            produto(2, "Com motor", estoque = 5, pontoReposicao = "10.00"),
        )

        val alertas = alertaService.listar(1)

        assertEquals(listOf(2), alertas.map { it.produtoId })
    }

    @Test
    fun `alerta expoe o lead time padrao do motor`() {
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produto(1, "Arroz", estoque = 5, pontoReposicao = "10.00"),
        )

        val alertas = alertaService.listar(1)

        assertEquals(MotorService.LEAD_TIME_PADRAO, alertas.single().leadTimeMedio)
    }

    @Test
    fun `sem produtos retorna lista vazia`() {
        every { produtoRepository.findByEstabelecimentoId(1) } returns emptyList()

        assertTrue(alertaService.listar(1).isEmpty())
    }
}