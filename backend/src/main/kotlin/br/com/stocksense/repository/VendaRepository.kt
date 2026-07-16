package br.com.stocksense.repository

import br.com.stocksense.domain.Venda
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime

interface VendaRepository : JpaRepository<Venda, Int> {

    @Modifying(clearAutomatically = true)
    @Query("DELETE FROM Venda v WHERE v.produtoId = :produtoId AND v.dataHora BETWEEN :inicio AND :fim")
    fun deleteByProdutoIdAndDataHoraBetween(
        @Param("produtoId") produtoId: Int,
        @Param("inicio") inicio: LocalDateTime,
        @Param("fim") fim: LocalDateTime,
    ): Int

    /**
     * Agrega as vendas de um produto em totais diários (uma linha por dia),
     * ordenadas cronologicamente. O ml-service espera uma série diária — enviar
     * registros individuais com datas repetidas quebraria o Holt-Winters.
     */
    @Query(
        """
        SELECT CAST(v.dataHora AS date) AS data, SUM(v.quantidade) AS total
        FROM Venda v
        WHERE v.produtoId = :produtoId
        GROUP BY CAST(v.dataHora AS date)
        ORDER BY CAST(v.dataHora AS date)
        """,
    )
    fun agregarVendasDiarias(@Param("produtoId") produtoId: Int): List<VendaDiariaProjecao>

    /**
     * Soma faturamento (valor_venda) e quantidade por produto, restrito aos
     * produtos de um estabelecimento. Alimenta o cálculo da Curva ABC.
     * `faturamento` vem nulo quando todo o histórico do produto está sem valor_venda.
     */
    @Query(
        """
        SELECT v.produtoId AS produtoId,
               SUM(v.valorVenda) AS faturamento,
               SUM(v.quantidade) AS quantidade
        FROM Venda v
        WHERE v.produtoId IN (
            SELECT p.produtoId FROM Produto p WHERE p.estabelecimentoId = :estabelecimentoId
        )
        GROUP BY v.produtoId
        """,
    )
    fun agregarFaturamentoPorProduto(
        @Param("estabelecimentoId") estabelecimentoId: Int,
    ): List<FaturamentoProdutoProjecao>

    /**
     * Soma o faturamento (valor_venda) por dia a partir de uma data, restrito aos
     * produtos do estabelecimento. O agrupamento por semana é feito no service
     * (testável em unidade e independente de função de data do MySQL).
     */
    @Query(
        """
        SELECT CAST(v.dataHora AS date) AS data, SUM(v.valorVenda) AS total
        FROM Venda v
        WHERE v.dataHora >= :inicio
          AND v.produtoId IN (
              SELECT p.produtoId FROM Produto p WHERE p.estabelecimentoId = :estabelecimentoId
          )
        GROUP BY CAST(v.dataHora AS date)
        ORDER BY CAST(v.dataHora AS date)
        """,
    )
    fun agregarFaturamentoDiario(
        @Param("estabelecimentoId") estabelecimentoId: Int,
        @Param("inicio") inicio: LocalDateTime,
    ): List<FaturamentoDiarioProjecao>
}

/** Projeção de venda agregada por dia (`agregarVendasDiarias`). */
interface VendaDiariaProjecao {
    val data: LocalDate
    val total: Long
}

/** Projeção de faturamento e quantidade por produto (`agregarFaturamentoPorProduto`). */
interface FaturamentoProdutoProjecao {
    val produtoId: Int
    val faturamento: BigDecimal?
    val quantidade: Long
}

/** Projeção de faturamento agregado por dia (`agregarFaturamentoDiario`). */
interface FaturamentoDiarioProjecao {
    val data: LocalDate
    val total: BigDecimal?
}
