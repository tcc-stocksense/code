package br.com.stocksense.repository

import br.com.stocksense.domain.Venda
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.time.LocalDateTime

interface VendaRepository : JpaRepository<Venda, Int> {

    @Modifying(clearAutomatically = true)
    @Query("DELETE FROM Venda v WHERE v.produtoId = :produtoId AND v.dataHora BETWEEN :inicio AND :fim")
    fun deleteByProdutoIdAndDataHoraBetween(
        @Param("produtoId") produtoId: Int,
        @Param("inicio") inicio: LocalDateTime,
        @Param("fim") fim: LocalDateTime,
    ): Int
}
