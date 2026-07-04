package br.com.stocksense.repository

import br.com.stocksense.domain.Previsao
import org.springframework.data.jpa.repository.JpaRepository

interface PrevisaoRepository : JpaRepository<Previsao, Int>
