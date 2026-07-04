package br.com.stocksense.client.dto

import com.fasterxml.jackson.databind.PropertyNamingStrategies
import com.fasterxml.jackson.databind.annotation.JsonNaming
import java.time.LocalDate

/**
 * Contrato de entrada do `POST /predict` do ml-service. Espelha o Pydantic
 * `PredictRequest`. O ml-service usa snake_case no JSON — `@JsonNaming` faz a
 * ponte a partir do camelCase do Kotlin, sem alterar o ObjectMapper global.
 */
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy::class)
data class PredictRequest(
    val produtoId: Int,
    val historico: List<VendaDiaria>,
    val leadTimeMedio: Int,
    val variabilidadeLeadTime: Double,
    val nivelServicoAlvo: Double,
    val estoqueAtual: Int,
    val isPromocional: List<Int> = emptyList(),
)

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy::class)
data class VendaDiaria(
    val data: LocalDate,
    val quantidade: Int,
)
