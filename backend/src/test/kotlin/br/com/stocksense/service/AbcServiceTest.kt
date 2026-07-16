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

    // ── curvaAbc (T-33) ────────────────────────────────────────────────────────

    private fun produtoClassificado(id: Int, nome: String, classe: String?): Produto =
        Produto(produtoId = id, estabelecimentoId = 1, nome = nome, estoqueAtual = 0, classeAbc = classe)

    @Test
    fun `curvaAbc ordena por faturamento e calcula percentuais individual e acumulado`() {
        every { vendaRepository.agregarFaturamentoPorProduto(1) } returns listOf(
            faturamento(20, BigDecimal("40.00"), 40),
            faturamento(10, BigDecimal("60.00"), 60),
        )
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produtoClassificado(10, "Arroz", "A"),
            produtoClassificado(20, "Feijão", "B"),
        )

        val curva = abcService.curvaAbc(1)

        assertFalse(curva.abcProxy)
        assertEquals(listOf(10, 20), curva.itens.map { it.produtoId })
        assertEquals(BigDecimal("60.0000"), curva.itens[0].percentualDoTotal)
        assertEquals(BigDecimal("60.0000"), curva.itens[0].percentualAcumulado)
        assertEquals(BigDecimal("40.0000"), curva.itens[1].percentualDoTotal)
        assertEquals(BigDecimal("100.0000"), curva.itens[1].percentualAcumulado)
        assertEquals("A", curva.itens[0].classeAbc)
        assertEquals("Arroz", curva.itens[0].nome)
    }

    @Test
    fun `curvaAbc sinaliza proxy quando falta valor_venda`() {
        every { vendaRepository.agregarFaturamentoPorProduto(1) } returns listOf(
            faturamento(10, null, 80),
            faturamento(20, null, 20),
        )
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produtoClassificado(10, "Arroz", "A"),
            produtoClassificado(20, "Feijão", "C"),
        )

        val curva = abcService.curvaAbc(1)

        assertTrue(curva.abcProxy)
        assertEquals(BigDecimal("80.0000"), curva.itens[0].percentualDoTotal)
    }

    @Test
    fun `curvaAbc ignora produto sem classe_abc preenchida`() {
        every { vendaRepository.agregarFaturamentoPorProduto(1) } returns listOf(
            faturamento(10, BigDecimal("60.00"), 60),
            faturamento(20, BigDecimal("40.00"), 40),
        )
        every { produtoRepository.findByEstabelecimentoId(1) } returns listOf(
            produtoClassificado(10, "Arroz", "A"),
            produtoClassificado(20, "Feijão", null), // motor/ABC ainda não classificou
        )

        val curva = abcService.curvaAbc(1)

        assertEquals(listOf(10), curva.itens.map { it.produtoId })
    }

    @Test
    fun `curvaAbc sem vendas retorna curva vazia`() {
        every { vendaRepository.agregarFaturamentoPorProduto(1) } returns emptyList()

        val curva = abcService.curvaAbc(1)

        assertFalse(curva.abcProxy)
        assertTrue(curva.itens.isEmpty())
    }
}
