package br.com.stocksense.dto.response

import java.time.LocalDateTime

data class MotorRecalculoResponse(
    val produtosProcessados: Int,
    val produtosComFalha: Int,
    val produtosClassificadosAbc: Int,
    val abcProxy: Boolean,
    val executadoEm: LocalDateTime,
)
