package br.com.stocksense.client.dto

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.databind.PropertyNamingStrategies
import com.fasterxml.jackson.databind.annotation.JsonNaming
import java.math.BigDecimal
import java.time.LocalDate

/**
 * Contrato de saída do `POST /predict` do ml-service. Espelha o Pydantic
 * `PredictResponse`.
 *
 * `@JsonIgnoreProperties(ignoreUnknown = true)`: o ml-service ainda devolve
 * `classe_abc` e `abc_proxy` (dívida técnica — ABC migrou para o backend, ADR #3),
 * que aqui são deliberadamente ignorados. `desvio_padrao_demanda` não é devolvido
 * pelo ml-service (decisão T-05 pendente) e por isso não consta neste contrato.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy::class)
data class PredictResponse(
    val produtoId: Int,
    val modeloSelecionado: String,
    val previsoes: List<PrevisaoDiaria>,
    val metricas: Map<String, MetricasModelo>,
    val pontoReposicao: BigDecimal,
    val estoqueSeguranca: BigDecimal,
    val diasAteRuptura: BigDecimal? = null,
    val aviso: String? = null,
)

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy::class)
data class PrevisaoDiaria(
    val data: LocalDate,
    val quantidadePrevista: BigDecimal,
)

data class MetricasModelo(
    val mape: BigDecimal,
    val rmse: BigDecimal,
    val mae: BigDecimal,
)
