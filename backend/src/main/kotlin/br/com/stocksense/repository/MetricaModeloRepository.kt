package br.com.stocksense.repository

import br.com.stocksense.domain.MetricaModelo
import org.springframework.data.jpa.repository.JpaRepository

interface MetricaModeloRepository : JpaRepository<MetricaModelo, Int>
