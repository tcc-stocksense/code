package br.com.stocksense.domain

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDateTime

@Entity
@Table(name = "produto")
class Produto(
    @Id
    @Column(name = "produto_id")
    val produtoId: Int,

    @Column(nullable = false, length = 100)
    var nome: String,

    @Column(name = "estoque_atual", nullable = false)
    var estoqueAtual: Int,

    @Column(length = 50)
    var categoria: String? = null,

    @Column(name = "unidade_medida", length = 10)
    var unidadeMedida: String? = null,

    @Column(name = "preco_custo", precision = 10, scale = 2)
    var precoCusto: BigDecimal? = null,

    @Column(name = "preco_venda", precision = 10, scale = 2)
    var precoVenda: BigDecimal? = null,

    @Column(name = "nivel_servico_alvo", precision = 5, scale = 2)
    var nivelServicoAlvo: BigDecimal = BigDecimal("0.95"),

    // campos calculados pelo motor preditivo — nunca recebidos via planilha
    @Column(name = "classe_abc", length = 1)
    var classeAbc: String? = null,

    @Column(name = "desvio_padrao_demanda", precision = 10, scale = 4)
    var desvioPadraoDemanda: BigDecimal? = null,

    @Column(name = "ponto_reposicao", precision = 10, scale = 2)
    var pontoReposicao: BigDecimal? = null,

    @Column(name = "estoque_seguranca", precision = 10, scale = 2)
    var estoqueSeguranca: BigDecimal? = null,

    @Column(name = "data_ultimo_calculo")
    var dataUltimoCalculo: LocalDateTime? = null,
)
