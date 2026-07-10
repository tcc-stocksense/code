package br.com.stocksense.service

import br.com.stocksense.client.MlServiceClient
import br.com.stocksense.client.dto.PredictRequest
import br.com.stocksense.client.dto.VendaDiaria
import br.com.stocksense.domain.MetricaModelo
import br.com.stocksense.domain.Previsao
import br.com.stocksense.domain.Produto
import br.com.stocksense.exception.MotorPreditivoException
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.MetricaModeloRepository
import br.com.stocksense.repository.PrevisaoRepository
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaRepository
import feign.FeignException
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class MotorService(
    private val produtoRepository: ProdutoRepository,
    private val vendaRepository: VendaRepository,
    private val previsaoRepository: PrevisaoRepository,
    private val metricaRepository: MetricaModeloRepository,
    private val mlServiceClient: MlServiceClient,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    /** IDs dos produtos de um estabelecimento — usado pelo controller para orquestrar o lote. */
    @Transactional(readOnly = true)
    fun listarProdutoIds(estabelecimentoId: Int): List<Int> =
        produtoRepository.findByEstabelecimentoId(estabelecimentoId).map { it.produtoId }

    companion object {
        // Defaults do Guia de Importação quando não há vínculo produto×fornecedor.
        // Enquanto ProdutoFornecedor não existir, todo produto usa estes valores.
        private const val LEAD_TIME_PADRAO = 3
        private const val VARIABILIDADE_LEAD_TIME_PADRAO = 1.0
    }

    /**
     * Executa o motor preditivo para um produto e persiste o resultado numa
     * única transação: 30 pontos em `previsao`, 2 linhas em `metrica_modelo`
     * (uma por modelo, com a flag `selecionado`) e os KPIs de estoque em `produto`.
     *
     * O motor acumula (append): cada execução grava com um novo `executadoEm`;
     * a rodada atual é sempre a de maior `executadoEm`.
     */
    @Transactional
    fun executarMotor(produtoId: Int) {
        val produto = produtoRepository.findByProdutoId(produtoId)
            ?: throw RecursoNaoEncontradoException("Produto $produtoId não encontrado.")

        val resp = try {
            mlServiceClient.predict(montarRequest(produto))
        } catch (ex: FeignException) {
            log.error("Falha ao chamar ml-service para produto {}", produtoId, ex)
            throw MotorPreditivoException("Serviço de previsão indisponível. Tente novamente em instantes.")
        }

        val agora = LocalDateTime.now()

        previsaoRepository.saveAll(
            resp.previsoes.map { p ->
                Previsao(
                    produtoId = produtoId,
                    dataPrevisao = p.data,
                    quantidadePrevista = p.quantidadePrevista,
                    modeloUtilizado = resp.modeloSelecionado,
                    executadoEm = agora,
                )
            },
        )

        metricaRepository.saveAll(
            resp.metricas.map { (modelo, m) ->
                MetricaModelo(
                    produtoId = produtoId,
                    modelo = modelo,
                    mape = m.mape,
                    rmse = m.rmse,
                    mae = m.mae,
                    selecionado = modelo == resp.modeloSelecionado,
                    executadoEm = agora,
                )
            },
        )

        produto.pontoReposicao = resp.pontoReposicao
        produto.estoqueSeguranca = resp.estoqueSeguranca
        produto.desvioPadraoDemanda = resp.desvioPadraoDemanda
        produto.dataUltimoCalculo = agora
        produtoRepository.save(produto)

        log.info(
            "Motor executado para produto {}: modelo={}, {} previsões, {} métricas",
            produtoId, resp.modeloSelecionado, resp.previsoes.size, resp.metricas.size,
        )
    }

    private fun montarRequest(produto: Produto): PredictRequest {
        val historico = vendaRepository.agregarVendasDiarias(produto.produtoId).map { v ->
            VendaDiaria(data = v.data, quantidade = v.total.toInt())
        }
        return PredictRequest(
            produtoId = produto.produtoId,
            historico = historico,
            leadTimeMedio = LEAD_TIME_PADRAO,
            variabilidadeLeadTime = VARIABILIDADE_LEAD_TIME_PADRAO,
            nivelServicoAlvo = produto.nivelServicoAlvo.toDouble(),
            estoqueAtual = produto.estoqueAtual,
        )
    }
}
