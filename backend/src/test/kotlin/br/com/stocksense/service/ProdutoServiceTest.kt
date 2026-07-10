package br.com.stocksense.service

import br.com.stocksense.domain.Produto
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.ProdutoRepository
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class ProdutoServiceTest {

    private val produtoRepository = mockk<ProdutoRepository>()
    private lateinit var produtoService: ProdutoService

    @BeforeTest
    fun setUp() {
        produtoService = ProdutoService(produtoRepository)
    }

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
}
