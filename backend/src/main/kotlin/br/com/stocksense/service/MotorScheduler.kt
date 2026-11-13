package br.com.stocksense.service

import br.com.stocksense.repository.EstabelecimentoRepository
import org.slf4j.LoggerFactory
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component

/**
 * Recálculo mensal automático (T-35) — o terceiro e último gatilho do motor, ao lado do
 * disparo manual e do pós-importação. Todos entram pelo mesmo `processarLoteMotor`.
 *
 * Roda para **todos** os estabelecimentos: num `@Scheduled` não existe requisição nem JWT,
 * então o `estabelecimentoId` vem do catálogo, não do contexto de segurança. Hoje há um só
 * cadastrado (ADR #4), mas varrer todos é o que o ADR #5 (preparado para multi-estabelecimento)
 * pede — e evita que ligar o segundo mercado passe despercebido.
 *
 * Desligável por `motor.scheduler.enabled=false`, útil em desenvolvimento e nos ambientes
 * onde o recálculo automático não é desejado.
 */
@Component
@ConditionalOnProperty(
    name = ["motor.scheduler.enabled"],
    havingValue = "true",
    matchIfMissing = true,
)
class MotorScheduler(
    private val estabelecimentoRepository: EstabelecimentoRepository,
    private val motorLoteService: MotorLoteService,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    /**
     * Dia 1 de cada mês, às 3h. O fuso é **explícito**: os containers rodam em UTC e, sem
     * `zone`, "3h" viraria meia-noite no horário de Brasília — perto o bastante da virada
     * do mês para cair no dia errado a cada mudança de horário. Cron e fuso são
     * configuráveis para que a infra ajuste sem recompilar.
     *
     * O lote é pesado (~0,5 s por produto, ver `docs/benchmark-motor.md`), por isso o
     * horário ocioso.
     */
    @Scheduled(
        cron = "\${motor.scheduler.cron:0 0 3 1 * *}",
        zone = "\${motor.scheduler.zone:America/Sao_Paulo}",
    )
    fun recalcularMensal() {
        val estabelecimentos = estabelecimentoRepository.findAll()

        log.info("Recálculo mensal iniciado para {} estabelecimento(s)", estabelecimentos.size)

        var comSucesso = 0
        var pulados = 0
        var comFalha = 0
        var produtosProcessados = 0

        for (estabelecimento in estabelecimentos) {
            try {
                // Pula (sem erro) se já houver lote em andamento — o guard da T-52.
                val resultado = motorLoteService.processarLoteSeOcioso(estabelecimento.id)
                if (resultado == null) {
                    pulados++
                } else {
                    comSucesso++
                    produtosProcessados += resultado.produtosProcessados
                }
            } catch (ex: Exception) {
                // Um estabelecimento que falha não pode derrubar os demais — mesma regra
                // que o lote aplica produto a produto.
                log.error("Recálculo mensal falhou para estabelecimento {}", estabelecimento.id, ex)
                comFalha++
            }
        }

        log.info(
            "Recálculo mensal concluído: {} estabelecimento(s) recalculado(s) ({} produtos), " +
                "{} pulado(s) por lote em andamento, {} com falha",
            comSucesso, produtosProcessados, pulados, comFalha,
        )
    }
}
