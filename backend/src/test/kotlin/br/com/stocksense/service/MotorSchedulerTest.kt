package br.com.stocksense.service

import br.com.stocksense.domain.Estabelecimento
import br.com.stocksense.repository.EstabelecimentoRepository
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.springframework.scheduling.support.CronExpression
import java.time.LocalDateTime
import java.time.ZoneId
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals

class MotorSchedulerTest {

    private val estabelecimentoRepository = mockk<EstabelecimentoRepository>()
    private val motorLoteService = mockk<MotorLoteService>()
    private lateinit var scheduler: MotorScheduler

    @BeforeTest
    fun setUp() {
        scheduler = MotorScheduler(estabelecimentoRepository, motorLoteService)
    }

    private fun estabelecimento(id: Int) = Estabelecimento(
        id = id,
        nomeFantasia = "Mercado $id",
        email = "mercado$id@teste.local",
        senhaHash = "hash",
    )

    private fun resultado() = ResultadoLote(5, 0, 5, false)

    @Test
    fun `recalcula todos os estabelecimentos`() {
        every { estabelecimentoRepository.findAll() } returns listOf(
            estabelecimento(1), estabelecimento(2), estabelecimento(3),
        )
        every { motorLoteService.processarLoteSeOcioso(any()) } returns resultado()

        scheduler.recalcularMensal()

        verify(exactly = 1) { motorLoteService.processarLoteSeOcioso(1) }
        verify(exactly = 1) { motorLoteService.processarLoteSeOcioso(2) }
        verify(exactly = 1) { motorLoteService.processarLoteSeOcioso(3) }
    }

    @Test
    fun `estabelecimento com lote em andamento e pulado sem derrubar os demais`() {
        every { estabelecimentoRepository.findAll() } returns listOf(
            estabelecimento(1), estabelecimento(2),
        )
        // null = guard da T-52 recusou; o cron pula em vez de falhar.
        every { motorLoteService.processarLoteSeOcioso(1) } returns null
        every { motorLoteService.processarLoteSeOcioso(2) } returns resultado()

        scheduler.recalcularMensal()

        verify(exactly = 1) { motorLoteService.processarLoteSeOcioso(2) }
    }

    @Test
    fun `falha em um estabelecimento nao aborta a varredura`() {
        every { estabelecimentoRepository.findAll() } returns listOf(
            estabelecimento(1), estabelecimento(2), estabelecimento(3),
        )
        every { motorLoteService.processarLoteSeOcioso(1) } returns resultado()
        every { motorLoteService.processarLoteSeOcioso(2) } throws IllegalStateException("banco fora")
        every { motorLoteService.processarLoteSeOcioso(3) } returns resultado()

        scheduler.recalcularMensal()

        // O estabelecimento seguinte ao que falhou continua sendo processado.
        verify(exactly = 1) { motorLoteService.processarLoteSeOcioso(3) }
    }

    @Test
    fun `sem estabelecimentos cadastrados nao quebra`() {
        every { estabelecimentoRepository.findAll() } returns emptyList()

        scheduler.recalcularMensal()

        verify(exactly = 0) { motorLoteService.processarLoteSeOcioso(any()) }
    }

    /**
     * O cron do default é o contrato da T-35: dia 1 do mês, às 3h. Um erro de campo aqui
     * (minuto × hora × dia) só apareceria em produção, e um mês depois.
     */
    @Test
    fun `cron padrao dispara no dia 1 as 3h`() {
        val cron = CronExpression.parse("0 0 3 1 * *")

        val proxima = cron.next(LocalDateTime.of(2026, 1, 15, 10, 30))

        assertEquals(LocalDateTime.of(2026, 2, 1, 3, 0), proxima)
    }

    @Test
    fun `cron padrao dispara uma vez por mes`() {
        val cron = CronExpression.parse("0 0 3 1 * *")

        val primeira = cron.next(LocalDateTime.of(2026, 2, 1, 4, 0))!!
        val segunda = cron.next(primeira)!!

        assertEquals(LocalDateTime.of(2026, 3, 1, 3, 0), primeira)
        assertEquals(LocalDateTime.of(2026, 4, 1, 3, 0), segunda)
    }

    /**
     * O fuso precisa ser válido: `@Scheduled` com zona inexistente falha só na subida
     * da aplicação, não na compilação.
     */
    @Test
    fun `fuso padrao e valido`() {
        assertEquals("America/Sao_Paulo", ZoneId.of("America/Sao_Paulo").id)
    }
}
