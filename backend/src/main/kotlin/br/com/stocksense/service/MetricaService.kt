package br.com.stocksense.service

import br.com.stocksense.dto.response.MetricaResponse
import br.com.stocksense.dto.response.toResponse
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.MetricaModeloRepository
import br.com.stocksense.repository.ProdutoRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

/**
 * Comparativo de modelos preditivos (Tela 10). Expõe as métricas MAPE/RMSE/MAE da
 * execução mais recente do motor para um produto — uma linha por modelo, com o
 * vencedor marcado em `selecionado`.
 */
@Service
class MetricaService(
    private val produtoRepository: ProdutoRepository,
    private val metricaModeloRepository: MetricaModeloRepository,
) {

    /**
     * Retorna as métricas mais recentes do produto. Lista vazia quando o motor ainda
     * não rodou para ele. Lança [RecursoNaoEncontradoException] se o produto não
     * existir ou pertencer a outro estabelecimento.
     */
    @Transactional(readOnly = true)
    fun metricas(estabelecimentoId: Int, produtoId: Int): List<MetricaResponse> {
        produtoRepository.findByProdutoId(produtoId)
            ?.takeIf { it.estabelecimentoId == estabelecimentoId }
            ?: throw RecursoNaoEncontradoException("Produto $produtoId não encontrado.")

        return metricaModeloRepository.findMetricasMaisRecentes(produtoId)
            .sortedByDescending { it.selecionado }
            .map { it.toResponse() }
    }
}