package br.com.stocksense.service

import br.com.stocksense.exception.MotorEmExecucaoException
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

class MotorJobStatusTest {

    private val jobStatus = MotorJobStatus()

    private val estabelecimentoId = 1

    @Test
    fun `estabelecimento que nunca rodou o motor esta PENDENTE`() {
        val job = jobStatus.consultar(99)

        assertEquals(EstadoJob.PENDENTE, job.estado)
        assertEquals(0, job.feitos)
        assertEquals(0, job.total)
        assertNull(job.iniciadoEm)
    }

    @Test
    fun `iniciar job marca PROCESSANDO e registra o inicio`() {
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)

        val job = jobStatus.consultar(estabelecimentoId)
        assertEquals(EstadoJob.PROCESSANDO, job.estado)
        assertNotNull(job.iniciadoEm)
    }

    @Test
    fun `segundo disparo no mesmo estabelecimento e recusado`() {
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)

        assertFailsWith<MotorEmExecucaoException> {
            jobStatus.iniciarJobOuConflitar(estabelecimentoId)
        }
    }

    @Test
    fun `guard e por estabelecimento - outro estabelecimento nao e bloqueado`() {
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)

        // Não deve lançar: o lote do estabelecimento 2 é independente.
        jobStatus.iniciarJobOuConflitar(2)

        assertEquals(EstadoJob.PROCESSANDO, jobStatus.consultar(estabelecimentoId).estado)
        assertEquals(EstadoJob.PROCESSANDO, jobStatus.consultar(2).estado)
    }

    @Test
    fun `concluir libera o guard e guarda o resumo`() {
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)
        val resultado = ResultadoLote(10, 1, 9, false)

        jobStatus.concluir(estabelecimentoId, resultado)

        val job = jobStatus.consultar(estabelecimentoId)
        assertEquals(EstadoJob.CONCLUIDO, job.estado)
        assertEquals(resultado, job.resumo)
        assertNotNull(job.concluidoEm)
        // Guard liberado: um novo lote pode começar.
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)
    }

    @Test
    fun `falhar libera o guard - erro nao trava o motor ate o restart`() {
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)

        jobStatus.falhar(estabelecimentoId)

        assertEquals(EstadoJob.FALHOU, jobStatus.consultar(estabelecimentoId).estado)
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)
    }

    @Test
    fun `progresso e total sao refletidos no estado`() {
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)
        jobStatus.definirTotal(estabelecimentoId, 30)
        jobStatus.atualizarProgresso(estabelecimentoId, 7, 30)

        val job = jobStatus.consultar(estabelecimentoId)
        assertEquals(7, job.feitos)
        assertEquals(30, job.total)
        assertEquals(EstadoJob.PROCESSANDO, job.estado)
    }

    @Test
    fun `tentarIniciarJob devolve false em vez de lancar - caminho do cron`() {
        assertTrue(jobStatus.tentarIniciarJob(estabelecimentoId))
        assertTrue(!jobStatus.tentarIniciarJob(estabelecimentoId))
    }

    /**
     * O guard só vale se for atômico. Com 20 threads disparando ao mesmo tempo, exatamente
     * uma pode sair com o job — se `compute` não fosse atômico, duas leriam PENDENTE antes
     * de qualquer escrita e o motor rodaria em duplicata.
     */
    @Test
    fun `disparos concorrentes - exatamente um vence`() {
        val threads = 20
        val largada = CountDownLatch(1)
        val chegada = CountDownLatch(threads)
        val vencedores = AtomicInteger(0)
        val pool = Executors.newFixedThreadPool(threads)

        repeat(threads) {
            pool.submit {
                largada.await()
                if (jobStatus.tentarIniciarJob(estabelecimentoId)) {
                    vencedores.incrementAndGet()
                }
                chegada.countDown()
            }
        }

        largada.countDown()
        assertTrue(chegada.await(10, TimeUnit.SECONDS), "threads não terminaram a tempo")
        pool.shutdown()

        assertEquals(1, vencedores.get())
    }
}
