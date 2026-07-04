package br.com.stocksense.repository

import br.com.stocksense.domain.Produto
import org.springframework.data.jpa.repository.JpaRepository

interface ProdutoRepository : JpaRepository<Produto, Int> {
    fun findByProdutoId(produtoId: Int): Produto?
    fun findByEstabelecimentoId(estabelecimentoId: Int): List<Produto>
}
