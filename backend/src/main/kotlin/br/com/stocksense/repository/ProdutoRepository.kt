package br.com.stocksense.repository

import br.com.stocksense.domain.Produto
import org.springframework.data.jpa.repository.JpaRepository
import java.math.BigDecimal

interface ProdutoRepository : JpaRepository<Produto, Int> {
    fun findByProdutoId(produtoId: Int): Produto?
    fun findByEstabelecimentoId(estabelecimentoId: Int): List<Produto>

    /** Produtos em risco: dias até ruptura menor ou igual ao limite (KPI "risco de faltar"). */
    fun countByEstabelecimentoIdAndDiasAteRupturaLessThanEqual(
        estabelecimentoId: Int,
        limite: BigDecimal,
    ): Long

    /** Produtos críticos: dias até ruptura estritamente abaixo do limite (KPI "crítico agora"). */
    fun countByEstabelecimentoIdAndDiasAteRupturaLessThan(
        estabelecimentoId: Int,
        limite: BigDecimal,
    ): Long
}
