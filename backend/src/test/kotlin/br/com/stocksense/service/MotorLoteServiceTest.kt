package br.com.stocksense.service

import br.com.stocksense.exception.MotorPreditivoException
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import io.mockk.verifyOrder
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class MotorLoteServiceTest {

    private val motorService = mockk<MotorService>()
    private val abcService = mockk<AbcService>()
    private lateinit var loteService: MotorLoteService

    private val estabelecimentoId = 1

    @BeforeTest
    fun setUp() {
        loteService = MotorLoteService(motorService, abcService)
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
}
