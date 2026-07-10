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
 * `@JsonIgnoreProperties(ignoreUnknown = true)`: mantido por tolerância a campos
 * futuros — o ml-service removeu `classe_abc`/`abc_proxy` do response (a dívida
 * técnica da ADR #3 foi resolvida do lado dele; nunca existiram neste DTO).
 * `desvio_padrao_demanda` (T-05) passou a ser devolvido pelo ml-service e agora
 * é mapeado abaixo.
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
    val desvioPadraoDemanda: BigDecimal? = null,
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
