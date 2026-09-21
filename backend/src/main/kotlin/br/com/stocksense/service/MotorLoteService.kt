package br.com.stocksense.service

import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service

/**
 * Resultado de uma execução do lote do motor.
 *
 * @property produtosProcessados produtos cujo motor rodou sem erro.
 * @property produtosComFalha produtos que falharam isoladamente (não abortam o lote).
 * @property produtosClassificadosAbc quantos tiveram `classe_abc` atualizada.
 * @property abcProxy true quando a ABC caiu para quantidade como proxy do faturamento.
 */
data class ResultadoLote(
    val produtosProcessados: Int,
    val produtosComFalha: Int,
    val produtosClassificadosAbc: Int,
    val abcProxy: Boolean,
)

/**
 * Núcleo compartilhado do lote do motor: roda `executarMotor` produto a produto e,
 * ao fim, recalcula a Curva ABC do estabelecimento.
 *
 * As cascas que o consomem (o `POST /api/motor/recalcular` de hoje e, adiante, o
 * disparo pós-importação e o cron mensal) são invólucros finos em volta deste método.
 *
 * **Por que um bean separado e não um método do `MotorService`:** o contrato do lote é
 * que cada produto rode na *sua própria* transação, para que uma falha isolada não
 * aborte os demais. `@Transactional` do Spring funciona por proxy, então uma chamada
 * de dentro do próprio `MotorService` a `executarMotor` seria auto-invocação e passaria
 * ao largo do proxy — todos os produtos cairiam na transação do chamador (ou em nenhuma).
 * Injetando o `MotorService` aqui, a chamada atravessa o proxy e cada produto mantém a
 * sua transação.
 *
 * Por isso este método **não** é `@Transactional`: uma transação envolvendo o lote
 * inteiro reintroduziria exatamente o acoplamento que o desenho evita.
 */
@Service
class MotorLoteService(
    private val motorService: MotorService,
    private val abcService: AbcService,
    private val jobStatus: MotorJobStatus,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    /**
     * Processa todos os produtos do estabelecimento e recalcula a ABC.
     *
     * **Guard de concorrência (T-52):** o job é tomado aqui dentro, antes de qualquer
     * trabalho. O guard vive no núcleo — e não em cada gatilho — para que manual,
     * pós-importação e cron passem todos por ele sem chance de desvio.
     *
     * @param onProgress chamado após cada produto (com ou sem falha) com o total já
     *   tentado e o total do lote. O `MotorJobStatus` é alimentado de qualquer forma;
     *   este callback é para quem quiser acompanhar por fora.
     * @throws br.com.stocksense.exception.MotorEmExecucaoException se já houver lote em
     *   andamento para o estabelecimento (vira `409 Conflict`). Quem prefere pular a
     *   falhar — o cron — deve checar antes com `MotorJobStatus.tentarIniciarJob`.
     */
    fun processarLoteMotor(
        estabelecimentoId: Int,
        onProgress: (feitos: Int, total: Int) -> Unit = { _, _ -> },
    ): ResultadoLote {
        // Fora do try: se o guard recusar, o job em andamento é de OUTRO chamador —
        // marcar FALHOU aqui destruiria o estado de um lote que está passando bem.
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)

        try {
            val produtoIds = motorService.listarProdutoIds(estabelecimentoId)
            val total = produtoIds.size
            jobStatus.definirTotal(estabelecimentoId, total)

            log.info("Lote do motor iniciado para estabelecimento {}: {} produtos", estabelecimentoId, total)

            var processados = 0
            var falhas = 0
            var feitos = 0
            for (produtoId in produtoIds) {
                try {
                    motorService.executarMotor(produtoId)
                    processados++
                } catch (ex: Exception) {
                    log.warn("Motor falhou para produto {}: {}", produtoId, ex.message)
                    falhas++
                }
                feitos++
                jobStatus.atualizarProgresso(estabelecimentoId, feitos, total)
                onProgress(feitos, total)
            }

            val abc = abcService.recalcularAbc(estabelecimentoId)

            val resultado = ResultadoLote(
                produtosProcessados = processados,
                produtosComFalha = falhas,
                produtosClassificadosAbc = abc.produtosClassificados,
                abcProxy = abc.abcProxy,
            )

            jobStatus.concluir(estabelecimentoId, resultado)

            log.info(
                "Lote do motor concluído para estabelecimento {}: {} processados, {} falhas, {} classificados na ABC",
                estabelecimentoId, processados, falhas, abc.produtosClassificados,
            )

            return resultado
        } catch (ex: Exception) {
            // Falha do lote inteiro (a ABC, por exemplo — a falha POR PRODUTO é tratada
            // no loop). Libera o guard: sem isto, um erro travaria o motor até o restart.
            log.error("Lote do motor falhou para estabelecimento {}", estabelecimentoId, ex)
            jobStatus.falhar(estabelecimentoId)
            throw ex
        }
    }
}
