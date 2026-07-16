package br.com.stocksense.service

import br.com.stocksense.dto.response.AbcItemResponse
import br.com.stocksense.dto.response.CurvaAbcResponse
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaRepository
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode

/**
 * Resultado de uma execução da classificação ABC.
 *
 * @property produtosClassificados quantos produtos tiveram `classe_abc` atualizada.
 * @property abcProxy true quando a classificação usou `quantidade` como proxy do
 *   faturamento (algum produto sem `valor_venda` no histórico) — limitação a expor.
 */
data class AbcResultado(
    val produtosClassificados: Int,
    val abcProxy: Boolean,
)

/**
 * Classificação ABC — ranking relativo entre TODOS os produtos do estabelecimento
 * por representatividade no faturamento (corte em 80% / 95% acumulado). Vive no
 * backend porque o `/predict` do ml-service opera por produto e não vê o catálogo
 * nem o `valor_venda` (ADR #3).
 */
@Service
class AbcService(
    private val vendaRepository: VendaRepository,
    private val produtoRepository: ProdutoRepository,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    companion object {
        private const val LIMITE_CLASSE_A = 80.0
        private const val LIMITE_CLASSE_B = 95.0
        private const val ESCALA_PERCENTUAL = 4
    }

    private data class ItemRanking(val produtoId: Int, val valor: Double)

    @Transactional
    fun recalcularAbc(estabelecimentoId: Int): AbcResultado {
        val agregados = vendaRepository.agregarFaturamentoPorProduto(estabelecimentoId)
        if (agregados.isEmpty()) {
            log.info("ABC: nenhum produto com vendas para estabelecimento {}", estabelecimentoId)
            return AbcResultado(0, false)
        }

        // Faturamento vem nulo quando o produto não tem nenhum valor_venda no histórico.
        // Se qualquer produto está sem faturamento, o ranking por receita fica inconsistente
        // (unidades diferentes), então caímos para quantidade como proxy em todos.
        val abcProxy = agregados.any { it.faturamento == null }
        if (abcProxy) {
            log.warn(
                "ABC: valor_venda ausente em ao menos um produto do estabelecimento {} — " +
                    "usando quantidade como proxy do faturamento",
                estabelecimentoId,
            )
        }

        val ranking = agregados
            .map { row ->
                val valor = if (abcProxy) row.quantidade.toDouble() else (row.faturamento?.toDouble() ?: 0.0)
                ItemRanking(row.produtoId, valor)
            }
            .sortedByDescending { it.valor }

        val total = ranking.sumOf { it.valor }
        if (total <= 0.0) {
            log.info("ABC: total de {} é zero — nada a classificar", if (abcProxy) "quantidade" else "faturamento")
            return AbcResultado(0, abcProxy)
        }

        var acumulado = 0.0
        var classificados = 0
        ranking.forEachIndexed { index, item ->
            acumulado += item.valor
            val percentualAcumulado = acumulado / total * 100.0
            val classe = when {
                index == 0 -> "A" // produto mais representativo (ou único) é sempre A
                percentualAcumulado <= LIMITE_CLASSE_A -> "A"
                percentualAcumulado <= LIMITE_CLASSE_B -> "B"
                else -> "C"
            }
            val produto = produtoRepository.findByProdutoId(item.produtoId)
            if (produto != null) {
                produto.classeAbc = classe
                produtoRepository.save(produto)
                classificados++
            }
        }

        log.info(
            "ABC recalculada para estabelecimento {}: {} produtos classificados (proxy={})",
            estabelecimentoId, classificados, abcProxy,
        )
        return AbcResultado(classificados, abcProxy)
    }

    /**
     * Curva ABC / Pareto (Tela 7): ranking por faturamento decrescente com percentual
     * individual e acumulado. Mesmo critério de valor do `recalcularAbc` (proxy por
     * quantidade quando falta `valor_venda`). Só entram produtos com `classe_abc`
     * preenchida — a classe exibida é a persistida pelo recálculo, garantindo
     * consistência com o restante do sistema.
     */
    @Transactional(readOnly = true)
    fun curvaAbc(estabelecimentoId: Int): CurvaAbcResponse {
        val agregados = vendaRepository.agregarFaturamentoPorProduto(estabelecimentoId)
        if (agregados.isEmpty()) return CurvaAbcResponse(abcProxy = false, itens = emptyList())

        val abcProxy = agregados.any { it.faturamento == null }
        val produtosPorId = produtoRepository.findByEstabelecimentoId(estabelecimentoId)
            .associateBy { it.produtoId }

        data class ItemCurva(val produtoId: Int, val valor: Double, val faturamento: BigDecimal?)

        val ranking = agregados
            .map { row ->
                val valor = if (abcProxy) row.quantidade.toDouble() else (row.faturamento?.toDouble() ?: 0.0)
                ItemCurva(row.produtoId, valor, row.faturamento)
            }
            .sortedByDescending { it.valor }

        val total = ranking.sumOf { it.valor }
        if (total <= 0.0) return CurvaAbcResponse(abcProxy = abcProxy, itens = emptyList())

        var acumulado = 0.0
        val itens = ranking.mapNotNull { item ->
            acumulado += item.valor
            val produto = produtosPorId[item.produtoId] ?: return@mapNotNull null
            val classe = produto.classeAbc ?: return@mapNotNull null
            AbcItemResponse(
                produtoId = item.produtoId,
                nome = produto.nome,
                classeAbc = classe,
                faturamento = item.faturamento,
                percentualDoTotal = percentual(item.valor, total),
                percentualAcumulado = percentual(acumulado, total),
            )
        }

        return CurvaAbcResponse(abcProxy = abcProxy, itens = itens)
    }

    private fun percentual(valor: Double, total: Double): BigDecimal =
        BigDecimal.valueOf(valor / total * 100.0).setScale(ESCALA_PERCENTUAL, RoundingMode.HALF_UP)
}
