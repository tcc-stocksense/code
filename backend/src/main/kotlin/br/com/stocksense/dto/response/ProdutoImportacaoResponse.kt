package br.com.stocksense.dto.response

data class ProdutoImportacaoResponse(
    val totalLinhas: Int,
    val importados: Int,
    val erros: List<ErroLinha>,
)

data class ErroLinha(
    val linha: Int,
    val mensagem: String,
)
