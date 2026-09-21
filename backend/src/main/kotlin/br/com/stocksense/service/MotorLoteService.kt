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
) {
    private val log = LoggerFactory.getLogger(javaClass)

    /**
     * Processa todos os produtos do estabelecimento e recalcula a ABC.
     *
     * @param onProgress chamado após cada produto (com ou sem falha) com o total já
     *   tentado e o total do lote. Usado pelo acompanhamento de progresso; o default
     *   não faz nada, para quem só quer o resultado final.
     */
    fun processarLoteMotor(
        estabelecimentoId: Int,
        onProgress: (feitos: Int, total: Int) -> Unit = { _, _ -> },
    ): ResultadoLote {
        val produtoIds = motorService.listarProdutoIds(estabelecimentoId)
        val total = produtoIds.size

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
            onProgress(feitos, total)
        }

        val abc = abcService.recalcularAbc(estabelecimentoId)

        log.info(
            "Lote do motor concluído para estabelecimento {}: {} processados, {} falhas, {} classificados na ABC",
            estabelecimentoId, processados, falhas, abc.produtosClassificados,
        )

        return ResultadoLote(
            produtosProcessados = processados,
            produtosComFalha = falhas,
            produtosClassificadosAbc = abc.produtosClassificados,
            abcProxy = abc.abcProxy,
        )
    }
}
