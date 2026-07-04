package br.com.stocksense.domain

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDateTime

@Entity
@Table(name = "metrica_modelo")
class MetricaModelo(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "produto_id", nullable = false)
    val produtoId: Int,

    @Column(length = 50, nullable = false)
    val modelo: String,

    @Column(precision = 8, scale = 4)
    val mape: BigDecimal? = null,

    @Column(precision = 10, scale = 4)
    val rmse: BigDecimal? = null,

    @Column(precision = 10, scale = 4)
    val mae: BigDecimal? = null,

    @Column(nullable = false)
    val selecionado: Boolean = false,

    @Column(name = "executado_em", nullable = false)
    val executadoEm: LocalDateTime,
)
