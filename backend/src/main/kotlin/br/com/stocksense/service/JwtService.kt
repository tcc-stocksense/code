package br.com.stocksense.service

import br.com.stocksense.config.JwtConfig
import io.jsonwebtoken.JwtException
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.security.Keys
import org.springframework.stereotype.Service
import java.nio.charset.StandardCharsets
import java.util.Date
import javax.crypto.SecretKey

@Service
class JwtService(private val jwtConfig: JwtConfig) {

    private val key: SecretKey = Keys.hmacShaKeyFor(jwtConfig.secret.toByteArray(StandardCharsets.UTF_8))

    fun gerarToken(estabelecimentoId: Int): String {
        val agora = Date()
        val expiracao = Date(agora.time + jwtConfig.expirationMs)
        return Jwts.builder()
            .subject(estabelecimentoId.toString())
            .issuedAt(agora)
            .expiration(expiracao)
            .signWith(key)
            .compact()
    }

    fun validarToken(token: String): Boolean = try {
        Jwts.parser().verifyWith(key).build().parseSignedClaims(token)
        true
    } catch (ex: JwtException) {
        false
    } catch (ex: IllegalArgumentException) {
        false
    }

    fun extrairEstabelecimentoId(token: String): Int =
        Jwts.parser().verifyWith(key).build().parseSignedClaims(token).payload.subject.toInt()
}
