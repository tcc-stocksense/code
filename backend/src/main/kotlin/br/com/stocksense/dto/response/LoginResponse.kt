package br.com.stocksense.dto.response

data class LoginResponse(
    val token: String,
    val estabelecimentoId: Int,
    val nomeFantasia: String,
)