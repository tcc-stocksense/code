package br.com.stocksense.dto.response

data class VendaImportacaoResponse(
    val totalLinhas: Int,
    val importados: Int,
    val diasDeHistorico: Int,
    val erros: List<ErroLinha>,
    val avisos: List<String>,
)
