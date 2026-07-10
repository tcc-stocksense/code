package br.com.stocksense.service

import br.com.stocksense.domain.Produto
import br.com.stocksense.repository.FaturamentoProdutoProjecao
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaRepository
import io.mockk.every
import io.mockk.mockk
import java.math.BigDecimal
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class AbcServiceTest {

    private val vendaRepository = mockk<VendaRepository>()
    private val produtoRepository = mockk<ProdutoRepository>()
    private lateinit var abcService: AbcService

    private val produtos = mutableMapOf<Int, Produto>()

    @BeforeTest
    fun setUp() {
        abcService = AbcService(vendaRepository, produtoRepository)
        produtos.clear()
        every { produtoRepository.findByProdutoId(any()) } answers {
            produtos.getOrPut(firstArg()) { Produto(produtoId = firstArg(), nome = "P${firstArg<Int>()}", estoqueAtual = 0) }
        }
        every { produtoRepository.save(any()) } answers { firstArg() }
    }

    private fun faturamento(id: Int, faturamento: BigDecimal?, quantidade: Long): FaturamentoProdutoProjecao =
        object : FaturamentoProdutoProjecao {
            override val produtoId = id
            override val faturamento = faturamento
            override val quantidade = quantidade
        }

    @Test
    fun `classifica A B C respeitando os limites acumulados de 80 e 95 por cento`() {
        // Faturamentos somam 100 → % acumulada bate exatamente nos limites 80 e 95.
        every { vendaRepository.agregarFaturamentoPorProduto(1) } returns listOf(
            faturamento(10, BigDecimal("60.00"), 60), // cum 60% → A
            faturamento(20, BigDecimal("20.00"), 20), // cum 80% → A (limite inclusivo)
            faturamento(30, BigDecimal("15.00"), 15), // cum 95% → B (limite inclusivo)
            faturamento(40, BigDecimal("5.00"), 5),   // cum 100% → C
        )

        val resultado = abcService.recalcularAbc(1)

        assertEquals(4, resultado.produtosClassificados)
        assertFalse(resultado.abcProxy)
        assertEquals("A", produtos.getValue(10).classeAbc)
        assertEquals("A", produtos.getValue(20).classeAbc)
        assertEquals("B", produtos.getValue(30).classeAbc)
        assertEquals("C", produtos.getValue(40).classeAbc)
    }

    @Test
    fun `produto unico sempre recebe classe A mesmo representando 100 por cento`() {
        every { vendaRepository.agregarFaturamentoPorProduto(1) } returns listOf(
            faturamento(7, BigDecimal("500.00"), 500),
        )

        val resultado = abcService.recalcularAbc(1)

        assertEquals("A", produtos.getValue(7).classeAbc)
        assertFalse(resultado.abcProxy)
    }

    @Test
    fun `usa quantidade como proxy quando faturamento esta ausente`() {
        every { vendaRepository.agregarFaturamentoPorProduto(1) } returns listOf(
            faturamento(10, null, 80), // cum 80% → A
            faturamento(20, null, 20), // cum 100% → C (não há valor_venda; ranking por quantidade)
        )

        val resultado = abcService.recalcularAbc(1)

        assertTrue(resultado.abcProxy)
        assertEquals("A", produtos.getValue(10).classeAbc)
        assertEquals("C", produtos.getValue(20).classeAbc)
    }

    @Test
    fun `retorna zero classificados quando nao ha vendas`() {
        every { vendaRepository.agregarFaturamentoPorProduto(1) } returns emptyList()

        val resultado = abcService.recalcularAbc(1)

        assertEquals(0, resultado.produtosClassificados)
        assertFalse(resultado.abcProxy)
    }
}
