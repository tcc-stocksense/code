package br.com.stocksense.dto.response

import java.math.BigDecimal

/**
 * Curva ABC / Pareto (Tela 7). `abcProxy = true` sinaliza que o ranking usou
 * `quantidade` como substituto do faturamento (histórico sem `valor_venda`) —
 * limitação a expor na tela, conforme CLAUDE.md do backend §6.
 */
data class CurvaAbcResponse(
    val abcProxy: Boolean,
    val itens: List<AbcItemResponse>,
)

/** Um produto no ranking ABC, com participação individual e acumulada. */
data class AbcItemResponse(
    val produtoId: Int,
    val nome: String,
    val classeAbc: String,
    val faturamento: BigDecimal?,
    val percentualDoTotal: BigDecimal,
    val percentualAcumulado: BigDecimal,
)