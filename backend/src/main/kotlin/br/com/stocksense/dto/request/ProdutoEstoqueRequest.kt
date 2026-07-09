package br.com.stocksense.dto.request

import jakarta.validation.constraints.PositiveOrZero

data class ProdutoEstoqueRequest(
    @field:PositiveOrZero(message = "O estoque não pode ser negativo.")
    val estoqueAtual: Int,
)
