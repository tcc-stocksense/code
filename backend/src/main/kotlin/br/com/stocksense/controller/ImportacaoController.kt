package br.com.stocksense.controller

import br.com.stocksense.dto.response.ProdutoImportacaoResponse
import br.com.stocksense.dto.response.VendaImportacaoResponse
import br.com.stocksense.service.ProdutoImportacaoService
import br.com.stocksense.service.VendaImportacaoService
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.multipart.MultipartFile

@RestController
@RequestMapping("/api/importacao")
class ImportacaoController(
    private val produtoImportacaoService: ProdutoImportacaoService,
    private val vendaImportacaoService: VendaImportacaoService,
) {

    @PostMapping("/produtos")
    @ResponseStatus(HttpStatus.CREATED)
    fun importarProdutos(
        @RequestParam("arquivo") arquivo: MultipartFile,
    ): ProdutoImportacaoResponse = produtoImportacaoService.importar(arquivo)

    @PostMapping("/vendas")
    @ResponseStatus(HttpStatus.CREATED)
    fun importarVendas(
        @RequestParam("arquivo") arquivo: MultipartFile,
    ): VendaImportacaoResponse = vendaImportacaoService.importar(arquivo)
}
