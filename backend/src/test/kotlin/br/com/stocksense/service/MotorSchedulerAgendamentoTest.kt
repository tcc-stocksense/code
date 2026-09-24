package br.com.stocksense.service

import br.com.stocksense.repository.EstabelecimentoRepository
import io.mockk.mockk
import org.springframework.boot.autoconfigure.AutoConfigurations
import org.springframework.boot.autoconfigure.task.TaskSchedulingAutoConfiguration
import org.springframework.boot.test.context.runner.ApplicationContextRunner
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.scheduling.annotation.EnableScheduling
import org.springframework.scheduling.config.ScheduledTaskHolder
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * O `@Scheduled` do `MotorScheduler` usa placeholders (`${motor.scheduler.cron}`) que só
 * são resolvidos na subida da aplicação — um cron malformado, um fuso inexistente ou um
 * nome de propriedade errado não quebram a compilação nem os testes unitários, quebram o
 * boot em produção. Estes testes sobem um contexto Spring mínimo (sem banco, sem web) só
 * para exercitar esse registro.
 */
class MotorSchedulerAgendamentoTest {

    @Configuration
    @EnableScheduling
    class ContextoDeAgendamento {
        @Bean
        fun estabelecimentoRepository(): EstabelecimentoRepository = mockk(relaxed = true)

        @Bean
        fun motorLoteService(): MotorLoteService = mockk(relaxed = true)

        @Bean
        fun motorScheduler(
            estabelecimentoRepository: EstabelecimentoRepository,
            motorLoteService: MotorLoteService,
        ) = MotorScheduler(estabelecimentoRepository, motorLoteService)
    }

    private val runner = ApplicationContextRunner()
        .withConfiguration(AutoConfigurations.of(TaskSchedulingAutoConfiguration::class.java))
        .withUserConfiguration(ContextoDeAgendamento::class.java)

    @Test
    fun `tarefa e registrada com os defaults da aplicacao`() {
        runner.run { context ->
            assertTrue(context.startupFailure == null, "contexto falhou: ${context.startupFailure?.message}")

            val tarefas = context.getBean(ScheduledTaskHolder::class.java).scheduledTasks
            assertEquals(1, tarefas.size)
            assertTrue(
                tarefas.first().task.toString().contains("recalcularMensal"),
                "a tarefa agendada nao e o recalcularMensal",
            )
        }
    }

    @Test
    fun `cron e fuso configurados por propriedade sao aceitos`() {
        runner
            .withPropertyValues(
                "motor.scheduler.cron=0 30 4 2 * *",
                "motor.scheduler.zone=UTC",
            )
            .run { context ->
                assertTrue(context.startupFailure == null, "contexto falhou: ${context.startupFailure?.message}")
                assertEquals(1, context.getBean(ScheduledTaskHolder::class.java).scheduledTasks.size)
            }
    }

    @Test
    fun `cron malformado derruba o contexto - a validacao existe de fato`() {
        runner
            .withPropertyValues("motor.scheduler.cron=isto nao e um cron")
            .run { context ->
                assertTrue(context.startupFailure != null, "cron invalido deveria ter derrubado o contexto")
            }
    }
}
