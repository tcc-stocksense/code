package br.com.stocksense.repository

import br.com.stocksense.domain.Estabelecimento
import org.springframework.data.jpa.repository.JpaRepository

interface EstabelecimentoRepository : JpaRepository<Estabelecimento, Int> {
    fun findByEmail(email: String): Estabelecimento?
}