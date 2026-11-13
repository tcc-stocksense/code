package br.com.stocksense.service

import br.com.stocksense.exception.MotorEmExecucaoException
import br.com.stocksense.exception.MotorPreditivoException
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import io.mockk.verifyOrder
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

class MotorLoteServiceTest {

    private val motorService = mockk<MotorService>()
    private val abcService = mockk<AbcService>()

    // Real, nao mock: o guard e o objeto sob teste nos cenarios de concorrencia,
    // e nos demais o seu comportamento real (tomar e liberar o job) e o esperado.
    private val jobStatus = MotorJobStatus()
    private lateinit var loteService: MotorLoteService

    private val estabelecimentoId = 1

    @BeforeTest
    fun setUp() {
        loteService = MotorLoteService(motorService, abcService, jobStatus)
    }

    @Test
    fun `processa todos os produtos e recalcula a ABC`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10, 20, 30)
        every { motorService.executarMotor(any()) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(3, false)

        val resultado = loteService.processarLoteMotor(estabelecimentoId)

        assertEquals(3, resultado.produtosProcessados)
        assertEquals(0, resultado.produtosComFalha)
        assertEquals(3, resultado.produtosClassificadosAbc)
        assertTrue(!resultado.abcProxy)
        verify(exactly = 1) { motorService.executarMotor(10) }
        verify(exactly = 1) { motorService.executarMotor(20) }
        verify(exactly = 1) { motorService.executarMotor(30) }
    }

    @Test
    fun `falha isolada nao aborta o lote`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10, 20, 30)
        every { motorService.executarMotor(10) } returns Unit
        every { motorService.executarMotor(20) } throws MotorPreditivoException("ml-service fora")
        every { motorService.executarMotor(30) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(2, false)

        val resultado = loteService.processarLoteMotor(estabelecimentoId)

        assertEquals(2, resultado.produtosProcessados)
        assertEquals(1, resultado.produtosComFalha)
        // O produto seguinte ao que falhou continua sendo processado.
        verify(exactly = 1) { motorService.executarMotor(30) }
    }

    @Test
    fun `ABC roda depois de todos os produtos`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10, 20)
        every { motorService.executarMotor(any()) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(2, false)

        loteService.processarLoteMotor(estabelecimentoId)

        verifyOrder {
            motorService.executarMotor(10)
            motorService.executarMotor(20)
            abcService.recalcularAbc(estabelecimentoId)
        }
    }

    @Test
    fun `onProgress e chamado a cada produto incluindo os que falham`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10, 20, 30)
        every { motorService.executarMotor(10) } returns Unit
        every { motorService.executarMotor(20) } throws MotorPreditivoException("ml-service fora")
        every { motorService.executarMotor(30) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(2, false)

        val progresso = mutableListOf<Pair<Int, Int>>()
        loteService.processarLoteMotor(estabelecimentoId) { feitos, total -> progresso += feitos to total }

        assertEquals(listOf(1 to 3, 2 to 3, 3 to 3), progresso)
    }

    @Test
    fun `lote sem produtos nao quebra e ainda chama a ABC`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns emptyList()
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(0, false)

        val resultado = loteService.processarLoteMotor(estabelecimentoId)

        assertEquals(0, resultado.produtosProcessados)
        assertEquals(0, resultado.produtosComFalha)
        assertEquals(0, resultado.produtosClassificadosAbc)
        verify(exactly = 1) { abcService.recalcularAbc(estabelecimentoId) }
    }

    @Test
    fun `abcProxy do AbcService atravessa para o resultado do lote`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10)
        every { motorService.executarMotor(10) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(1, true)

        val resultado = loteService.processarLoteMotor(estabelecimentoId)

        assertTrue(resultado.abcProxy)
    }

    @Test
    fun `lote concorrente no mesmo estabelecimento recebe conflito`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10)
        every { motorService.executarMotor(10) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(1, false)

        // Simula um lote já em andamento (o disparo concorrente que chegou primeiro).
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)

        assertFailsWith<MotorEmExecucaoException> {
            loteService.processarLoteMotor(estabelecimentoId)
        }
        // O guard recusou antes de qualquer trabalho.
        verify(exactly = 0) { motorService.executarMotor(any()) }
    }

    @Test
    fun `guard nao bloqueia estabelecimentos diferentes`() {
        every { motorService.listarProdutoIds(2) } returns listOf(10)
        every { motorService.executarMotor(10) } returns Unit
        every { abcService.recalcularAbc(2) } returns AbcResultado(1, false)

        jobStatus.iniciarJobOuConflitar(estabelecimentoId)

        val resultado = loteService.processarLoteMotor(2)

        assertEquals(1, resultado.produtosProcessados)
    }

    @Test
    fun `lote bem sucedido conclui o job e libera o guard`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10, 20)
        every { motorService.executarMotor(any()) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(2, false)

        val resultado = loteService.processarLoteMotor(estabelecimentoId)

        val job = jobStatus.consultar(estabelecimentoId)
        assertEquals(EstadoJob.CONCLUIDO, job.estado)
        assertEquals(2, job.feitos)
        assertEquals(2, job.total)
        assertEquals(resultado, job.resumo)
    }

    @Test
    fun `falha do lote inteiro marca FALHOU e libera o guard`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10)
        every { motorService.executarMotor(10) } returns Unit
        // A ABC roda fora do try-catch por produto: se ela explode, o lote inteiro falha.
        every { abcService.recalcularAbc(estabelecimentoId) } throws IllegalStateException("banco fora")

        assertFailsWith<IllegalStateException> {
            loteService.processarLoteMotor(estabelecimentoId)
        }

        assertEquals(EstadoJob.FALHOU, jobStatus.consultar(estabelecimentoId).estado)
        // Guard liberado: um erro nao pode travar o motor ate o restart.
        jobStatus.iniciarJobOuConflitar(estabelecimentoId)
    }

    @Test
    fun `progresso do lote e refletido no MotorJobStatus`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10, 20, 30)
        every { motorService.executarMotor(any()) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(3, false)

        val vistos = mutableListOf<Pair<Int, Int>>()
        loteService.processarLoteMotor(estabelecimentoId) { _, _ ->
            val j = jobStatus.consultar(estabelecimentoId)
            vistos += j.feitos to j.total
        }

        // O status ja esta atualizado quando o onProgress roda.
        assertEquals(listOf(1 to 3, 2 to 3, 3 to 3), vistos)
    }

    @Test
    fun `processarLoteSeOcioso devolve null em vez de lancar quando ha lote em andamento`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10)

        jobStatus.iniciarJobOuConflitar(estabelecimentoId)

        // Nao lanca: o cron nao pode quebrar porque chegou na hora errada.
        val resultado = loteService.processarLoteSeOcioso(estabelecimentoId)

        assertNull(resultado)
        verify(exactly = 0) { motorService.executarMotor(any()) }
    }

    @Test
    fun `processarLoteSeOcioso roda normalmente quando o motor esta ocioso`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10, 20)
        every { motorService.executarMotor(any()) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } returns AbcResultado(2, false)

        val resultado = loteService.processarLoteSeOcioso(estabelecimentoId)

        assertNotNull(resultado)
        assertEquals(2, resultado.produtosProcessados)
        assertEquals(EstadoJob.CONCLUIDO, jobStatus.consultar(estabelecimentoId).estado)
    }

    @Test
    fun `processarLoteSeOcioso propaga falha real do lote - so o conflito e silenciado`() {
        every { motorService.listarProdutoIds(estabelecimentoId) } returns listOf(10)
        every { motorService.executarMotor(10) } returns Unit
        every { abcService.recalcularAbc(estabelecimentoId) } throws IllegalStateException("banco fora")

        // Conflito de concorrencia vira null; erro de verdade continua subindo.
        assertFailsWith<IllegalStateException> {
            loteService.processarLoteSeOcioso(estabelecimentoId)
        }
    }
}
