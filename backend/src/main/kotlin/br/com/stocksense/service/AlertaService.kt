package br.com.stocksense.service

import br.com.stocksense.domain.Produto
import br.com.stocksense.dto.response.AlertaResponse
import br.com.stocksense.repository.ProdutoRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

/**
 * Alertas de reposição (Tela 5). O semáforo é relativo ao ponto de reposição
 * calculado pelo motor (não a cortes fixos de dias — ver mapeamento T4/T5).
 * Produtos sem `pontoReposicao` (motor ainda não rodou) ficam fora da lista:
 * sem o PR não há como classificar a urgência.
 */
@Service
class AlertaService(
    private val produtoRepository: ProdutoRepository,
) {

    companion object {
        const val SEMAFORO_VERMELHO = "VERMELHO"
        const val SEMAFORO_AMARELO = "AMARELO"
        const val SEMAFORO_VERDE = "VERDE"

        /** Fator do limiar amarelo: até PR × 1.5 o estoque ainda está próximo do PR. */
        private val FATOR_ATENCAO = BigDecimal("1.5")

        /** Ordem de urgência para o sort (menor = mais urgente). */
        private val PRIORIDADE = mapOf(SEMAFORO_VERMELHO to 0, SEMAFORO_AMARELO to 1, SEMAFORO_VERDE to 2)
    }

    /**
     * Lista os alertas do estabelecimento ordenados por urgência: vermelhos primeiro,
     * depois amarelos e verdes; dentro de cada grupo, menor `diasAteRuptura` primeiro
     * (nulos por último).
     */
    @Transactional(readOnly = true)
    fun listar(estabelecimentoId: Int): List<AlertaResponse> =
        produtoRepository.findByEstabelecimentoId(estabelecimentoId)
            .mapNotNull { it.toAlerta() }
            .sortedWith(
                compareBy(
                    { PRIORIDADE.getValue(it.semaforo) },
                    { it.diasAteRuptura == null },
                    { it.diasAteRuptura },
                ),
            )

    /** Null quando o motor ainda não calculou o ponto de reposição do produto. */
    private fun Produto.toAlerta(): AlertaResponse? {
        val pr = pontoReposicao ?: return null
        return AlertaResponse(
            produtoId = produtoId,
            nome = nome,
            estoqueAtual = estoqueAtual,
            pontoReposicao = pr,
            diasAteRuptura = diasAteRuptura,
            leadTimeMedio = MotorService.LEAD_TIME_PADRAO,
            semaforo = calcularSemaforo(estoqueAtual, pr),
        )
    }

    private fun calcularSemaforo(estoqueAtual: Int, pontoReposicao: BigDecimal): String {
        val estoque = BigDecimal(estoqueAtual)
        return when {
            estoque <= pontoReposicao -> SEMAFORO_VERMELHO
            estoque <= pontoReposicao.multiply(FATOR_ATENCAO) -> SEMAFORO_AMARELO
            else -> SEMAFORO_VERDE
        }
    }
}