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
@Table(name = "venda")
class Venda(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "produto_id", nullable = false)
    val produtoId: Int,

    @Column(name = "data_hora", nullable = false)
    var dataHora: LocalDateTime,

    @Column(nullable = false)
    var quantidade: Int,

    @Column(name = "valor_venda", precision = 10, scale = 2)
    var valorVenda: BigDecimal? = null,

    @Column(name = "is_promocional", nullable = false)
    var isPromocional: Short = 0,
)
