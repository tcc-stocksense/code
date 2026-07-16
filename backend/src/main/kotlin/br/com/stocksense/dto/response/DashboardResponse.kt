package br.com.stocksense.dto.response

import java.math.BigDecimal
import java.time.LocalDate

/**
 * KPIs do dashboard (Tela 2). `mapeMedioModeloSelecionado` é null quando o motor
 * nunca rodou; a acurácia exibida na tela é `100 − mape`.
 */
data class DashboardResponse(
    val riscoDeFaltar7Dias: Long,
    val criticoAgora: Long,
    val mapeMedioModeloSelecionado: BigDecimal?,
    val seriesFaturamento: List<SemanaFaturamentoResponse>,
)

/** Faturamento total de uma semana; `semana` é a segunda-feira que a inicia. */
data class SemanaFaturamentoResponse(
    val semana: LocalDate,
    val total: BigDecimal,
)