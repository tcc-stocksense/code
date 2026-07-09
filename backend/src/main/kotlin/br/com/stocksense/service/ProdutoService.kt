package br.com.stocksense.service

import br.com.stocksense.dto.response.ProdutoResponse
import br.com.stocksense.dto.response.toResponse
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.ProdutoRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class ProdutoService(
    private val produtoRepository: ProdutoRepository,
) {

    @Transactional(readOnly = true)
    fun listarTodos(estabelecimentoId: Int): List<ProdutoResponse> =
        produtoRepository.findByEstabelecimentoId(estabelecimentoId)
            .sortedBy { it.nome }
            .map { it.toResponse() }

    @Transactional
    fun atualizarEstoque(estabelecimentoId: Int, produtoId: Int, estoqueAtual: Int): ProdutoResponse {
        val produto = produtoRepository.findByProdutoId(produtoId)
            ?.takeIf { it.estabelecimentoId == estabelecimentoId }
            ?: throw RecursoNaoEncontradoException("Produto $produtoId não encontrado.")

        produto.estoqueAtual = estoqueAtual
        return produtoRepository.save(produto).toResponse()
    }
}
