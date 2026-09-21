package br.com.stocksense.controller

import br.com.stocksense.dto.response.MotorRecalculoResponse
import br.com.stocksense.service.MotorLoteService
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.time.LocalDateTime

@RestController
@RequestMapping("/api/motor")
class MotorController(
    private val motorLoteService: MotorLoteService,
) {

    /**
     * Dispara o motor preditivo para todos os produtos do estabelecimento autenticado
     * e, em seguida, recalcula a Curva ABC. Cada produto roda em sua própria transação:
     * uma falha isolada não aborta o lote inteiro.
     *
     * Síncrono: a resposta só volta quando o lote termina (ver `docs/benchmark-motor.md`
     * para o custo medido).
     */
    @PostMapping("/recalcular")
    fun recalcular(): MotorRecalculoResponse {
        val resultado = motorLoteService.processarLoteMotor(estabelecimentoAutenticado())

        return MotorRecalculoResponse(
            produtosProcessados = resultado.produtosProcessados,
            produtosComFalha = resultado.produtosComFalha,
            produtosClassificadosAbc = resultado.produtosClassificadosAbc,
            abcProxy = resultado.abcProxy,
            executadoEm = LocalDateTime.now(),
        )
    }

    private fun estabelecimentoAutenticado(): Int =
        SecurityContextHolder.getContext().authentication.principal as Int
}
