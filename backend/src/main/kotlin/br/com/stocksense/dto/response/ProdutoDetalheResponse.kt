package br.com.stocksense.dto.response

import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime

/**
 * Detalhe do produto para a Tela 6 (estatísticas + reposição).
 *
 * Os campos de previsão (`demandaMediaDiaria`, `coeficienteVariacao`, `diasAteRuptura`,
 * `previsoes`) e os KPIs de reposição vêm nulos/vazios quando o motor ainda não rodou
 * para o produto (histórico insuficiente ou primeira carga) — a tela deve sinalizar esse
 * estado em vez de assumir que todo produto tem previsão.
 */
data class ProdutoDetalheResponse(
    val produtoId: Int,
    val nome: String,
    val categoria: String?,
    val unidadeMedida: String?,
    val estoqueAtual: Int,
    val classeAbc: String?,

    // Estatísticas de demanda
    val demandaMediaDiaria: BigDecimal?,   // média dos pontos previstos mais recentes
    val desvioPadraoDemanda: BigDecimal?,  // σ calculado pelo motor (Ballou)
    val coeficienteVariacao: BigDecimal?,  // σ / demandaMedia (dispersão relativa)
    val tendenciaPercentual: BigDecimal?,  // variação % média dos primeiros 14 vs últimos 14 dias

    // KPIs de reposição (persistidos pelo motor)
    val pontoReposicao: BigDecimal?,
    val estoqueSeguranca: BigDecimal?,
    val diasAteRuptura: BigDecimal?,       // estoqueAtual / demandaMediaDiaria
    val dataUltimoCalculo: LocalDateTime?,

    // Série de previsão mais recente (até 30 pontos)
    val previsoes: List<PrevisaoPontoResponse>,
)

/** Um ponto da série de previsão de demanda. */
data class PrevisaoPontoResponse(
    val data: LocalDate,
    val quantidadePrevista: BigDecimal?,
)
