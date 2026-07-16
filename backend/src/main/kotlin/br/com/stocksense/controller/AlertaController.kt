package br.com.stocksense.controller

import br.com.stocksense.dto.response.AlertaResponse
import br.com.stocksense.service.AlertaService
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/alertas")
class AlertaController(private val alertaService: AlertaService) {

    @GetMapping
    fun listar(): List<AlertaResponse> =
        alertaService.listar(estabelecimentoAutenticado())

    private fun estabelecimentoAutenticado(): Int =
        SecurityContextHolder.getContext().authentication.principal as Int
}