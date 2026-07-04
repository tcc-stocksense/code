package br.com.stocksense.service

import br.com.stocksense.domain.Estabelecimento
import br.com.stocksense.dto.request.LoginRequest
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.EstabelecimentoRepository
import io.mockk.every
import io.mockk.mockk
import org.springframework.security.crypto.password.PasswordEncoder
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class AuthServiceTest {

    private val estabelecimentoRepository = mockk<EstabelecimentoRepository>()
    private val passwordEncoder = mockk<PasswordEncoder>()
    private val jwtService = mockk<JwtService>()
    private lateinit var authService: AuthService

    private val estabelecimento = Estabelecimento(
        id = 1,
        nomeFantasia = "Mercadinho do Zé",
        email = "ze@mercadinho.com",
        senhaHash = "hash-bcrypt",
    )

    @BeforeTest
    fun setUp() {
        authService = AuthService(estabelecimentoRepository, passwordEncoder, jwtService)
    }

    @Test
    fun `login com credenciais validas retorna token e dados do estabelecimento`() {
        every { estabelecimentoRepository.findByEmail("ze@mercadinho.com") } returns estabelecimento
        every { passwordEncoder.matches("senha123", "hash-bcrypt") } returns true
        every { jwtService.gerarToken(1) } returns "token-jwt"

        val response = authService.login(LoginRequest("ze@mercadinho.com", "senha123"))

        assertEquals("token-jwt", response.token)
        assertEquals(1, response.estabelecimentoId)
        assertEquals("Mercadinho do Zé", response.nomeFantasia)
    }

    @Test
    fun `login com email nao encontrado lanca RecursoNaoEncontradoException`() {
        every { estabelecimentoRepository.findByEmail("inexistente@mercadinho.com") } returns null

        assertFailsWith<RecursoNaoEncontradoException> {
            authService.login(LoginRequest("inexistente@mercadinho.com", "qualquer"))
        }
    }

    @Test
    fun `login com senha incorreta lanca a mesma excecao e mensagem do email inexistente`() {
        every { estabelecimentoRepository.findByEmail("ze@mercadinho.com") } returns estabelecimento
        every { passwordEncoder.matches("senhaErrada", "hash-bcrypt") } returns false
        every { estabelecimentoRepository.findByEmail("inexistente@mercadinho.com") } returns null

        val exSenhaErrada = assertFailsWith<RecursoNaoEncontradoException> {
            authService.login(LoginRequest("ze@mercadinho.com", "senhaErrada"))
        }
        val exEmailInexistente = assertFailsWith<RecursoNaoEncontradoException> {
            authService.login(LoginRequest("inexistente@mercadinho.com", "qualquer"))
        }

        assertEquals(exSenhaErrada.message, exEmailInexistente.message)
    }
}
