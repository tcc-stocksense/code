package br.com.stocksense.service

import br.com.stocksense.exception.MotorEmExecucaoException
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import java.time.LocalDateTime
import java.util.concurrent.ConcurrentHashMap

/** Estados do lote do motor — nomes congelados pelo contrato da T-42, consumido pelo front. */
enum class EstadoJob {
    PENDENTE,
    PROCESSANDO,
    CONCLUIDO,
    FALHOU,
}

/**
 * Fotografia do lote de um estabelecimento.
 *
 * @property feitos produtos já tentados (com ou sem falha).
 * @property total produtos do lote; 0 enquanto o catálogo não foi lido.
 * @property resumo preenchido só quando o lote termina (`CONCLUIDO`).
 */
data class JobMotor(
    val estado: EstadoJob,
    val feitos: Int = 0,
    val total: Int = 0,
    val iniciadoEm: LocalDateTime? = null,
    val concluidoEm: LocalDateTime? = null,
    val resumo: ResultadoLote? = null,
)

/**
 * Estado do lote do motor, em memória, por estabelecimento (T-40) — e o guard de
 * concorrência que protege os três gatilhos (T-52).
 *
 * **Limitação consciente, aprovada na validação de 2026-07-12:** o estado se perde num
 * restart da aplicação. O lote é idempotente e pode ser re-disparado manualmente, o que
 * torna uma tabela `execucao_motor` desnecessária no escopo do TCC. Um restart no meio de
 * um lote também libera o guard — aceitável, porque o processo que o segurava morreu junto.
 *
 * Thread-safe: todas as transições passam por `compute`, que o `ConcurrentHashMap` executa
 * atomicamente por chave. É isso que faz o guard funcionar — dois disparos simultâneos para
 * o mesmo estabelecimento serializam, e só o primeiro sai com o job.
 */
@Component
class MotorJobStatus {

    private val log = LoggerFactory.getLogger(javaClass)

    private val jobs = ConcurrentHashMap<Int, JobMotor>()

    /**
     * Guard dos gatilhos HTTP (manual e pós-importação): toma o job ou recusa.
     *
     * @throws MotorEmExecucaoException se já houver lote `PROCESSANDO` — vira `409 Conflict`.
     */
    fun iniciarJobOuConflitar(estabelecimentoId: Int) {
        if (!tentarIniciarJob(estabelecimentoId)) {
            throw MotorEmExecucaoException(
                "Já existe um recálculo em andamento para este estabelecimento. " +
                    "Aguarde a conclusão para disparar outro.",
            )
        }
    }

    /**
     * A tomada atômica em si, sem exceção — primitiva sobre a qual o
     * `iniciarJobOuConflitar` é construído, e à disposição de quem prefira ramificar a
     * falhar. O cron (T-35) chega aqui pelo `MotorLoteService.processarLoteSeOcioso`.
     *
     * @return true se este chamador ficou com o job.
     */
    fun tentarIniciarJob(estabelecimentoId: Int): Boolean {
        var obteve = false
        jobs.compute(estabelecimentoId) { _, atual ->
            if (atual?.estado == EstadoJob.PROCESSANDO) {
                atual
            } else {
                obteve = true
                JobMotor(estado = EstadoJob.PROCESSANDO, iniciadoEm = LocalDateTime.now())
            }
        }
        if (!obteve) {
            log.info("Guard do motor: lote já em andamento para estabelecimento {}", estabelecimentoId)
        }
        return obteve
    }

    /** Registra o tamanho do lote, assim que o catálogo é lido. */
    fun definirTotal(estabelecimentoId: Int, total: Int) {
        jobs.computeIfPresent(estabelecimentoId) { _, atual -> atual.copy(total = total) }
    }

    /** Avanço do lote — alimentado pelo `onProgress` do `processarLoteMotor`. */
    fun atualizarProgresso(estabelecimentoId: Int, feitos: Int, total: Int) {
        jobs.computeIfPresent(estabelecimentoId) { _, atual ->
            atual.copy(feitos = feitos, total = total)
        }
    }

    /** Fecha o job com sucesso e libera o guard. */
    fun concluir(estabelecimentoId: Int, resultado: ResultadoLote) {
        jobs.computeIfPresent(estabelecimentoId) { _, atual ->
            atual.copy(
                estado = EstadoJob.CONCLUIDO,
                concluidoEm = LocalDateTime.now(),
                resumo = resultado,
            )
        }
    }

    /** Fecha o job com falha e libera o guard — senão um erro travaria o motor para sempre. */
    fun falhar(estabelecimentoId: Int) {
        jobs.computeIfPresent(estabelecimentoId) { _, atual ->
            atual.copy(estado = EstadoJob.FALHOU, concluidoEm = LocalDateTime.now())
        }
    }

    /** Leitura do estado (T-42). Estabelecimento que nunca rodou o motor devolve `PENDENTE`. */
    fun consultar(estabelecimentoId: Int): JobMotor =
        jobs[estabelecimentoId] ?: JobMotor(estado = EstadoJob.PENDENTE)
}
