package br.com.stocksense.dto.response

import br.com.stocksense.domain.Produto
import java.math.BigDecimal
import java.time.LocalDateTime

data class ProdutoResponse(
    val produtoId: Int,
    val nome: String,
    val categoria: String?,
    val unidadeMedida: String?,
    val estoqueAtual: Int,
    val classeAbc: String?,
    val pontoReposicao: BigDecimal?,
    val estoqueSeguranca: BigDecimal?,
    val dataUltimoCalculo: LocalDateTime?,
)

fun Produto.toResponse(): ProdutoResponse = ProdutoResponse(
    produtoId = produtoId,
    nome = nome,
    categoria = categoria,
    unidadeMedida = unidadeMedida,
    estoqueAtual = estoqueAtual,
    classeAbc = classeAbc,
    pontoReposicao = pontoReposicao,
    estoqueSeguranca = estoqueSeguranca,
    dataUltimoCalculo = dataUltimoCalculo,
)
