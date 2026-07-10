package br.com.stocksense.controller

import br.com.stocksense.dto.request.ProdutoEstoqueRequest
import br.com.stocksense.dto.response.ProdutoResponse
import br.com.stocksense.service.ProdutoService
import jakarta.validation.Valid
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PatchMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/produtos")
class ProdutoController(private val produtoService: ProdutoService) {

    @GetMapping
    fun listar(): List<ProdutoResponse> =
        produtoService.listarTodos(estabelecimentoAutenticado())

    @PatchMapping("/{id}/estoque")
    fun atualizarEstoque(
        @PathVariable id: Int,
        @Valid @RequestBody request: ProdutoEstoqueRequest,
    ): ProdutoResponse =
        produtoService.atualizarEstoque(estabelecimentoAutenticado(), id, request.estoqueAtual)

    private fun estabelecimentoAutenticado(): Int =
        SecurityContextHolder.getContext().authentication.principal as Int
}
