package br.com.stocksense.service

import br.com.stocksense.dto.request.LoginRequest
import br.com.stocksense.dto.response.LoginResponse
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.EstabelecimentoRepository
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Service

@Service
class AuthService(
    private val estabelecimentoRepository: EstabelecimentoRepository,
    private val passwordEncoder: PasswordEncoder,
    private val jwtService: JwtService,
) {
    fun login(request: LoginRequest): LoginResponse {
        val estabelecimento = estabelecimentoRepository.findByEmail(request.email)
            ?: throw RecursoNaoEncontradoException(CREDENCIAIS_INVALIDAS)

        if (!passwordEncoder.matches(request.senha, estabelecimento.senhaHash)) {
            throw RecursoNaoEncontradoException(CREDENCIAIS_INVALIDAS)
        }

        val token = jwtService.gerarToken(estabelecimento.id)
        return LoginResponse(token, estabelecimento.id, estabelecimento.nomeFantasia)
    }

    companion object {
        private const val CREDENCIAIS_INVALIDAS = "E-mail ou senha inválidos."
    }
}