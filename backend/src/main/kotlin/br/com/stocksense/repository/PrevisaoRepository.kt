package br.com.stocksense.repository

import br.com.stocksense.domain.Previsao
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface PrevisaoRepository : JpaRepository<Previsao, Int> {

    /**
     * Retorna a previsão mais recente de um produto: as linhas gravadas na última
     * execução do motor (maior `executadoEm`), ordenadas por data. O motor grava em
     * append, então cada rodada compartilha o mesmo `executadoEm`; a mais recente é
     * a que interessa para a tela de detalhe.
     */
    @Query(
        """
        SELECT p FROM Previsao p
        WHERE p.produtoId = :produtoId
          AND p.executadoEm = (
              SELECT MAX(p2.executadoEm) FROM Previsao p2 WHERE p2.produtoId = :produtoId
          )
        ORDER BY p.dataPrevisao
        """,
    )
    fun findPrevisaoMaisRecente(@Param("produtoId") produtoId: Int): List<Previsao>
}
