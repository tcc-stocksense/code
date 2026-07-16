package br.com.stocksense.repository

import br.com.stocksense.domain.MetricaModelo
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface MetricaModeloRepository : JpaRepository<MetricaModelo, Int> {

    /**
     * Retorna as métricas da execução mais recente de um produto — as linhas com o
     * maior `executadoEm` (uma por modelo: Holt-Winters e Prophet). Alimenta a Tela 10
     * (comparativo de modelos).
     */
    @Query(
        """
        SELECT m FROM MetricaModelo m
        WHERE m.produtoId = :produtoId
          AND m.executadoEm = (
              SELECT MAX(m2.executadoEm) FROM MetricaModelo m2 WHERE m2.produtoId = :produtoId
          )
        """,
    )
    fun findMetricasMaisRecentes(@Param("produtoId") produtoId: Int): List<MetricaModelo>
}
