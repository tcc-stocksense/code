package br.com.stocksense.dto.response

import br.com.stocksense.domain.MetricaModelo
import java.math.BigDecimal
import java.time.LocalDateTime

/**
 * Métrica de avaliação de um modelo numa execução do motor. Alimenta a Tela 10
 * (comparativo Holt-Winters × Prophet). `selecionado` marca o modelo vencedor.
 */
data class MetricaResponse(
    val modelo: String,
    val mape: BigDecimal?,
    val rmse: BigDecimal?,
    val mae: BigDecimal?,
    val selecionado: Boolean,
    val executadoEm: LocalDateTime,
)

fun MetricaModelo.toResponse(): MetricaResponse = MetricaResponse(
    modelo = modelo,
    mape = mape,
    rmse = rmse,
    mae = mae,
    selecionado = selecionado,
    executadoEm = executadoEm,
)