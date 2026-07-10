package br.com.stocksense.service

import br.com.stocksense.domain.Produto
import br.com.stocksense.dto.response.PrevisaoPontoResponse
import br.com.stocksense.dto.response.ProdutoDetalheResponse
import br.com.stocksense.dto.response.ProdutoResponse
import br.com.stocksense.dto.response.toResponse
import br.com.stocksense.exception.RecursoNaoEncontradoException
import br.com.stocksense.repository.PrevisaoRepository
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaDiariaProjecao
import br.com.stocksense.repository.VendaRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode

@Service
class ProdutoService(
    private val produtoRepository: ProdutoRepository,
    private val previsaoRepository: PrevisaoRepository,
    private val vendaRepository: VendaRepository,
) {

    private companion object {
        const val ESCALA_DEMANDA = 2
        const val ESCALA_RAZAO = 4
        const val JANELA_TENDENCIA = 14
    }

    @Transactional(readOnly = true)
    fun listarTodos(estabelecimentoId: Int): List<ProdutoResponse> =
        produtoRepository.findByEstabelecimentoId(estabelecimentoId)
            .sortedBy { it.nome }
            .map { it.toResponse() }

    @Transactional
    fun atualizarEstoque(estabelecimentoId: Int, produtoId: Int, estoqueAtual: Int): ProdutoResponse {
        val produto = buscarDoEstabelecimento(estabelecimentoId, produtoId)
        produto.estoqueAtual = estoqueAtual
        return produtoRepository.save(produto).toResponse()
    }

    /**
     * Monta o detalhe do produto (Tela 6): identificação, estatísticas de demanda e
     * KPIs de reposição. A demanda média e os dias até ruptura são derivados da
     * previsão mais recente (o motor não persiste esses dois valores diretamente);
     * a tendência vem do histórico de vendas. Campos de previsão ficam nulos quando o
     * motor ainda não rodou para o produto.
     */
    @Transactional(readOnly = true)
    fun detalhe(estabelecimentoId: Int, produtoId: Int): ProdutoDetalheResponse {
        val produto = buscarDoEstabelecimento(estabelecimentoId, produtoId)

        val previsoes = previsaoRepository.findPrevisaoMaisRecente(produtoId)
        val demandaMedia = calcularDemandaMedia(previsoes.mapNotNull { it.quantidadePrevista })
        val diasAteRuptura = calcularDiasAteRuptura(produto.estoqueAtual, demandaMedia)
        val coeficienteVariacao = calcularCoeficienteVariacao(produto.desvioPadraoDemanda, demandaMedia)
        val tendencia = calcularTendencia(vendaRepository.agregarVendasDiarias(produtoId))

        return ProdutoDetalheResponse(
            produtoId = produto.produtoId,
            nome = produto.nome,
            categoria = produto.categoria,
            unidadeMedida = produto.unidadeMedida,
            estoqueAtual = produto.estoqueAtual,
            classeAbc = produto.classeAbc,
            demandaMediaDiaria = demandaMedia,
            desvioPadraoDemanda = produto.desvioPadraoDemanda,
            coeficienteVariacao = coeficienteVariacao,
            tendenciaPercentual = tendencia,
            pontoReposicao = produto.pontoReposicao,
            estoqueSeguranca = produto.estoqueSeguranca,
            diasAteRuptura = diasAteRuptura,
            dataUltimoCalculo = produto.dataUltimoCalculo,
            previsoes = previsoes.map {
                PrevisaoPontoResponse(data = it.dataPrevisao, quantidadePrevista = it.quantidadePrevista)
            },
        )
    }

    private fun buscarDoEstabelecimento(estabelecimentoId: Int, produtoId: Int): Produto =
        produtoRepository.findByProdutoId(produtoId)
            ?.takeIf { it.estabelecimentoId == estabelecimentoId }
            ?: throw RecursoNaoEncontradoException("Produto $produtoId não encontrado.")

    /** Média das quantidades previstas. Null quando não há previsão persistida. */
    private fun calcularDemandaMedia(quantidades: List<BigDecimal>): BigDecimal? {
        if (quantidades.isEmpty()) return null
        return quantidades.reduce(BigDecimal::add)
            .divide(BigDecimal(quantidades.size), ESCALA_DEMANDA, RoundingMode.HALF_UP)
    }

    /** Dias até ruptura = estoque / demanda média. Null quando a demanda é zero/ausente. */
    private fun calcularDiasAteRuptura(estoqueAtual: Int, demandaMedia: BigDecimal?): BigDecimal? =
        demandaMedia
            ?.takeIf { it.signum() > 0 }
            ?.let { BigDecimal(estoqueAtual).divide(it, ESCALA_DEMANDA, RoundingMode.HALF_UP) }

    /** Coeficiente de variação = σ / demanda média. Null quando a demanda é zero/ausente. */
    private fun calcularCoeficienteVariacao(desvio: BigDecimal?, demandaMedia: BigDecimal?): BigDecimal? {
        if (desvio == null) return null
        return demandaMedia
            ?.takeIf { it.signum() > 0 }
            ?.let { desvio.divide(it, ESCALA_RAZAO, RoundingMode.HALF_UP) }
    }

    /**
     * Tendência = variação percentual entre a média dos primeiros 14 e dos últimos 14
     * dias com venda. Null quando há menos de 28 dias (janelas se sobreporiam) ou
     * quando a média inicial é zero.
     */
    private fun calcularTendencia(serie: List<VendaDiariaProjecao>): BigDecimal? {
        if (serie.size < 2 * JANELA_TENDENCIA) return null
        val mediaPrimeiros = serie.take(JANELA_TENDENCIA).map { it.total }.average()
        val mediaUltimos = serie.takeLast(JANELA_TENDENCIA).map { it.total }.average()
        if (mediaPrimeiros == 0.0) return null
        val variacao = (mediaUltimos - mediaPrimeiros) / mediaPrimeiros * 100.0
        return BigDecimal.valueOf(variacao).setScale(ESCALA_RAZAO, RoundingMode.HALF_UP)
    }
}
