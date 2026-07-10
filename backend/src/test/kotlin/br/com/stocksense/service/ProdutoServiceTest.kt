package br.com.stocksense.service

import br.com.stocksense.domain.Previsao
import br.com.stocksense.domain.Produto
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.PrevisaoRepository
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaDiariaProjecao
import br.com.stocksense.repository.VendaRepository
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import kotlin.test.assertTrue

class ProdutoServiceTest {

    private val produtoRepository = mockk<ProdutoRepository>()
    private val previsaoRepository = mockk<PrevisaoRepository>()
    private val vendaRepository = mockk<VendaRepository>()
    private lateinit var produtoService: ProdutoService

    @BeforeTest
    fun setUp() {
        produtoService = ProdutoService(produtoRepository, previsaoRepository, vendaRepository)
    }

    private fun vendaDia(dia: LocalDate, total: Long): VendaDiariaProjecao =
        object : VendaDiariaProjecao {
            override val data = dia
            override val total = total
        }

    private fun previsao(data: LocalDate, quantidade: String?): Previsao =
        Previsao(
            produtoId = 1,
            dataPrevisao = data,
            quantidadePrevista = quantidade?.let { BigDecimal(it) },
            modeloUtilizado = "holt_winters",
            executadoEm = LocalDateTime.of(2025, 4, 1, 3, 0),
        )

    @Test
    fun `listarTodos retorna os produtos do estabelecimento ordenados por nome`() {
        val feijao = Produto(produtoId = 2, estabelecimentoId = 1, nome = "Feijão", estoqueAtual = 10)
        val arroz = Produto(produtoId = 1, estabelecimentoId = 1, nome = "Arroz", estoqueAtual = 40)
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(feijao, arroz)

        val response = produtoService.listarTodos(1)

        assertEquals(listOf("Arroz", "Feijão"), response.map { it.nome })
        assertEquals(listOf(1, 2), response.map { it.produtoId })
    }

    @Test
    fun `atualizarEstoque altera apenas o campo estoqueAtual e persiste`() {
        val produto = Produto(
            produtoId = 1,
            estabelecimentoId = 1,
            nome = "Arroz",
            estoqueAtual = 40,
            categoria = "Grãos",
        )
        every { produtoRepository.findByProdutoId(1) } returns produto
        val salvo = slot<Produto>()
        every { produtoRepository.save(capture(salvo)) } answers { salvo.captured }

        val response = produtoService.atualizarEstoque(estabelecimentoId = 1, produtoId = 1, estoqueAtual = 25)

        assertEquals(25, response.estoqueAtual)
        assertEquals("Arroz", response.nome)
        assertEquals("Grãos", response.categoria)
        verify { produtoRepository.save(produto) }
    }

    @Test
    fun `atualizarEstoque com produto inexistente lanca RecursoNaoEncontradoException`() {
        every { produtoRepository.findByProdutoId(99) } returns null

        assertFailsWith<RecursoNaoEncontradoException> {
            produtoService.atualizarEstoque(estabelecimentoId = 1, produtoId = 99, estoqueAtual = 10)
        }
    }

    @Test
    fun `atualizarEstoque de produto de outro estabelecimento lanca RecursoNaoEncontradoException`() {
        val produtoDeOutroEstabelecimento = Produto(
            produtoId = 5,
            estabelecimentoId = 2,
            nome = "Açúcar",
            estoqueAtual = 15,
        )
        every { produtoRepository.findByProdutoId(5) } returns produtoDeOutroEstabelecimento

        assertFailsWith<RecursoNaoEncontradoException> {
            produtoService.atualizarEstoque(estabelecimentoId = 1, produtoId = 5, estoqueAtual = 10)
        }
    }

    @Test
    fun `detalhe deriva demanda media, dias ate ruptura, CV e tendencia`() {
        val produto = Produto(
            produtoId = 1,
            estabelecimentoId = 1,
            nome = "Arroz",
            estoqueAtual = 40,
            categoria = "Grãos",
            classeAbc = "A",
            desvioPadraoDemanda = BigDecimal("2.50"),
            pontoReposicao = BigDecimal("55.00"),
            estoqueSeguranca = BigDecimal("15.00"),
        )
        every { produtoRepository.findByProdutoId(1) } returns produto
        // Média das previsões = (10 + 12 + 8) / 3 = 10.00
        every { previsaoRepository.findPrevisaoMaisRecente(1) } returns listOf(
            previsao(LocalDate.of(2025, 4, 1), "10.00"),
            previsao(LocalDate.of(2025, 4, 2), "12.00"),
            previsao(LocalDate.of(2025, 4, 3), "8.00"),
        )
        // 28 dias: primeiros 14 com total 10, últimos 14 com total 15 → +50%
        val serie = (0 until 14).map { vendaDia(LocalDate.of(2025, 1, 1).plusDays(it.toLong()), 10) } +
            (14 until 28).map { vendaDia(LocalDate.of(2025, 1, 1).plusDays(it.toLong()), 15) }
        every { vendaRepository.agregarVendasDiarias(1) } returns serie

        val detalhe = produtoService.detalhe(estabelecimentoId = 1, produtoId = 1)

        assertEquals(BigDecimal("10.00"), detalhe.demandaMediaDiaria)
        assertEquals(BigDecimal("4.00"), detalhe.diasAteRuptura)          // 40 / 10
        assertEquals(BigDecimal("0.2500"), detalhe.coeficienteVariacao)  // 2.50 / 10
        assertEquals(BigDecimal("50.0000"), detalhe.tendenciaPercentual) // (15-10)/10 * 100
        assertEquals("A", detalhe.classeAbc)
        assertEquals(BigDecimal("55.00"), detalhe.pontoReposicao)
        assertEquals(3, detalhe.previsoes.size)
    }

    @Test
    fun `detalhe sem previsao retorna campos de demanda nulos`() {
        val produto = Produto(
            produtoId = 1,
            estabelecimentoId = 1,
            nome = "Arroz",
            estoqueAtual = 40,
        )
        every { produtoRepository.findByProdutoId(1) } returns produto
        every { previsaoRepository.findPrevisaoMaisRecente(1) } returns emptyList()
        every { vendaRepository.agregarVendasDiarias(1) } returns emptyList()

        val detalhe = produtoService.detalhe(estabelecimentoId = 1, produtoId = 1)

        assertNull(detalhe.demandaMediaDiaria)
        assertNull(detalhe.diasAteRuptura)
        assertNull(detalhe.coeficienteVariacao)
        assertNull(detalhe.tendenciaPercentual)
        assertTrue(detalhe.previsoes.isEmpty())
    }

    @Test
    fun `detalhe com menos de 28 dias de venda nao calcula tendencia`() {
        val produto = Produto(produtoId = 1, estabelecimentoId = 1, nome = "Arroz", estoqueAtual = 40)
        every { produtoRepository.findByProdutoId(1) } returns produto
        every { previsaoRepository.findPrevisaoMaisRecente(1) } returns emptyList()
        every { vendaRepository.agregarVendasDiarias(1) } returns
            (0 until 20).map { vendaDia(LocalDate.of(2025, 1, 1).plusDays(it.toLong()), 10) }

        val detalhe = produtoService.detalhe(estabelecimentoId = 1, produtoId = 1)

        assertNull(detalhe.tendenciaPercentual)
    }

    @Test
    fun `detalhe com produto inexistente lanca RecursoNaoEncontradoException`() {
        every { produtoRepository.findByProdutoId(99) } returns null

        assertFailsWith<RecursoNaoEncontradoException> {
            produtoService.detalhe(estabelecimentoId = 1, produtoId = 99)
        }
    }

    @Test
    fun `detalhe de produto de outro estabelecimento lanca RecursoNaoEncontradoException`() {
        val produto = Produto(produtoId = 5, estabelecimentoId = 2, nome = "Açúcar", estoqueAtual = 15)
        every { produtoRepository.findByProdutoId(5) } returns produto

        assertFailsWith<RecursoNaoEncontradoException> {
            produtoService.detalhe(estabelecimentoId = 1, produtoId = 5)
        }
    }
}
