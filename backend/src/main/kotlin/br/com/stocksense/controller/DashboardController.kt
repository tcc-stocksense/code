package br.com.stocksense.controller

import br.com.stocksense.dto.response.DashboardResponse
import br.com.stocksense.service.DashboardService
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/dashboard")
class DashboardController(private val dashboardService: DashboardService) {

    @GetMapping
    fun resumo(): DashboardResponse =
        dashboardService.resumo(estabelecimentoAutenticado())

    private fun estabelecimentoAutenticado(): Int =
        SecurityContextHolder.getContext().authentication.principal as Int
}