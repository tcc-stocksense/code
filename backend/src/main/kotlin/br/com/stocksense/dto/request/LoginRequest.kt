package br.com.stocksense.dto.request

import jakarta.validation.constraints.NotBlank

data class LoginRequest(
    @field:NotBlank(message = "O e-mail é obrigatório.")
    val email: String,

    @field:NotBlank(message = "A senha é obrigatória.")
    val senha: String,
)
