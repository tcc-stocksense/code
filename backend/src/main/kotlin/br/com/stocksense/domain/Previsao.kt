package br.com.stocksense.domain

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime

@Entity
@Table(name = "previsao")
class Previsao(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "produto_id", nullable = false)
    val produtoId: Int,

    @Column(name = "data_previsao", nullable = false)
    val dataPrevisao: LocalDate,

    @Column(name = "quantidade_prevista", precision = 10, scale = 2)
    val quantidadePrevista: BigDecimal? = null,

    @Column(name = "modelo_utilizado", length = 50)
    val modeloUtilizado: String? = null,

    @Column(name = "executado_em", nullable = false)
    val executadoEm: LocalDateTime,
)
