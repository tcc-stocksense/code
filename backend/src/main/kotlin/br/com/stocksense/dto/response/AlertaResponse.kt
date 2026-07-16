package br.com.stocksense.dto.response

import java.math.BigDecimal

/**
 * Alerta de reposição de um produto (Tela 5). O semáforo é relativo ao ponto de
 * reposição calculado pelo motor — não a cortes fixos de dias:
 * VERMELHO (estoque ≤ PR), AMARELO (PR < estoque ≤ PR × 1.5), VERDE (acima).
 */
data class AlertaResponse(
    val produtoId: Int,
    val nome: String,
    val estoqueAtual: Int,
    val pontoReposicao: BigDecimal,
    val diasAteRuptura: BigDecimal?,
    val leadTimeMedio: Int,
    val semaforo: String,
)