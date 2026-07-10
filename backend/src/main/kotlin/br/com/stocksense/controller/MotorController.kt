package br.com.stocksense.controller

import br.com.stocksense.dto.response.MotorRecalculoResponse
import br.com.stocksense.service.AbcService
import br.com.stocksense.service.MotorService
import org.slf4j.LoggerFactory
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.time.LocalDateTime

@RestController
@RequestMapping("/api/motor")
class MotorController(
    private val motorService: MotorService,
    private val abcService: AbcService,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    /**
     * Dispara o motor preditivo para todos os produtos do estabelecimento autenticado
     * e, em seguida, recalcula a Curva ABC. Cada produto roda em sua própria transação
     * (via proxy do `MotorService`): uma falha isolada não aborta o lote inteiro.
     */
    @PostMapping("/recalcular")
    fun recalcular(): MotorRecalculoResponse {
        val estabelecimentoId = estabelecimentoAutenticado()
        val produtoIds = motorService.listarProdutoIds(estabelecimentoId)

        var processados = 0
        var falhas = 0
        for (produtoId in produtoIds) {
            try {
                motorService.executarMotor(produtoId)
                processados++
            } catch (ex: Exception) {
                log.warn("Motor falhou para produto {}: {}", produtoId, ex.message)
                falhas++
            }
        }

        val abc = abcService.recalcularAbc(estabelecimentoId)

        return MotorRecalculoResponse(
            produtosProcessados = processados,
            produtosComFalha = falhas,
            produtosClassificadosAbc = abc.produtosClassificados,
            abcProxy = abc.abcProxy,
            executadoEm = LocalDateTime.now(),
        )
    }

    private fun estabelecimentoAutenticado(): Int =
        SecurityContextHolder.getContext().authentication.principal as Int
}
