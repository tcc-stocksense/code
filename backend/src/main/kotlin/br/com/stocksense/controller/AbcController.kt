package br.com.stocksense.controller

import br.com.stocksense.dto.response.CurvaAbcResponse
import br.com.stocksense.service.AbcService
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/curva-abc")
class AbcController(private val abcService: AbcService) {

    @GetMapping
    fun curva(): CurvaAbcResponse =
        abcService.curvaAbc(estabelecimentoAutenticado())

    private fun estabelecimentoAutenticado(): Int =
        SecurityContextHolder.getContext().authentication.principal as Int
}