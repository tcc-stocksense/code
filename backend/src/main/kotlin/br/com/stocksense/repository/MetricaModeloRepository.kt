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

    /**
     * MAPE médio do modelo selecionado entre os produtos do estabelecimento,
     * considerando apenas a execução mais recente de cada produto (o motor grava em
     * append). Alimenta o KPI "acurácia do modelo" do dashboard — usa o modelo
     * vencedor por produto, nunca fixo num modelo só. Null quando o motor nunca rodou.
     */
    @Query(
        """
        SELECT AVG(m.mape) FROM MetricaModelo m
        WHERE m.selecionado = true
          AND m.produtoId IN (
              SELECT p.produtoId FROM Produto p WHERE p.estabelecimentoId = :estabelecimentoId
          )
          AND m.executadoEm = (
              SELECT MAX(m2.executadoEm) FROM MetricaModelo m2 WHERE m2.produtoId = m.produtoId
          )
        """,
    )
    fun mapeMedioSelecionado(@Param("estabelecimentoId") estabelecimentoId: Int): Double?
}
