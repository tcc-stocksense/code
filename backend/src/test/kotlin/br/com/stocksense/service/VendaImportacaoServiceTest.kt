package br.com.stocksense.service

import br.com.stocksense.exception.ImportacaoException
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaRepository
import io.mockk.every
import io.mockk.mockk
import org.apache.poi.xssf.usermodel.XSSFWorkbook
import org.springframework.mock.web.MockMultipartFile
import org.springframework.web.multipart.MultipartFile
import java.io.ByteArrayOutputStream
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class VendaImportacaoServiceTest {

    private val vendaRepository = mockk<VendaRepository>(relaxed = true)
    private val produtoRepository = mockk<ProdutoRepository>()
    private lateinit var service: VendaImportacaoService

    @BeforeTest
    fun setUp() {
        service = VendaImportacaoService(vendaRepository, produtoRepository)
        every { produtoRepository.existsById(any()) } returns true
    }

    private fun planilha(
        headers: List<String>,
        rows: List<List<Any?>>,
        filename: String = "5_vendas.xlsx",
    ): MultipartFile {
        val wb = XSSFWorkbook()
        val sheet = wb.createSheet("vendas")
        val header = sheet.createRow(0)
        headers.forEachIndexed { i, h -> header.createCell(i).setCellValue(h) }
        rows.forEachIndexed { r, row ->
            val excelRow = sheet.createRow(r + 1)
            row.forEachIndexed { c, value ->
                val cell = excelRow.createCell(c)
                when (value) {
                    null -> {}
                    is Number -> cell.setCellValue(value.toDouble())
                    else -> cell.setCellValue(value.toString())
                }
            }
        }
        val bos = ByteArrayOutputStream()
        wb.use { it.write(bos) }
        return MockMultipartFile(
            "arquivo", filename,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            bos.toByteArray(),
        )
    }

    private val cabecalho = listOf("produto_id", "data_hora", "quantidade", "valor_venda")

    @Test
    fun `importa vendas validas sem erros`() {
        val arquivo = planilha(
            cabecalho,
            listOf(
                listOf(1, "2025-01-01", 5, 100.00),
                listOf(1, "2025-01-02", 3, 60.00),
            ),
        )

        val resposta = service.importar(arquivo)

        assertEquals(2, resposta.totalLinhas)
        assertEquals(2, resposta.importados)
        assertTrue(resposta.erros.isEmpty())
    }

    @Test
    fun `acusa venda de produto inexistente`() {
        every { produtoRepository.existsById(999) } returns false
        val arquivo = planilha(cabecalho, listOf(listOf(999, "2025-01-01", 5, 100.00)))

        val resposta = service.importar(arquivo)

        assertEquals(0, resposta.importados)
        assertEquals(1, resposta.erros.size)
        assertTrue(resposta.erros.first().mensagem.contains("999"))
    }

    @Test
    fun `acusa data em formato invalido`() {
        val arquivo = planilha(cabecalho, listOf(listOf(1, "01/01/2025", 5, 100.00)))

        val resposta = service.importar(arquivo)

        assertEquals(0, resposta.importados)
        assertTrue(resposta.erros.any { it.mensagem.contains("data_hora") })
    }

    @Test
    fun `acusa quantidade menor ou igual a zero`() {
        val arquivo = planilha(cabecalho, listOf(listOf(1, "2025-01-01", 0, 100.00)))

        val resposta = service.importar(arquivo)

        assertEquals(0, resposta.importados)
        assertTrue(resposta.erros.any { it.mensagem.contains("quantidade") })
    }

    @Test
    fun `acusa valor_venda com virgula como separador decimal`() {
        val arquivo = planilha(cabecalho, listOf(listOf(1, "2025-01-01", 5, "37,80")))

        val resposta = service.importar(arquivo)

        assertEquals(0, resposta.importados)
        assertTrue(resposta.erros.any { it.mensagem.contains("valor_venda") })
    }

    @Test
    fun `avisa quando historico tem menos de 90 dias mas importa as vendas`() {
        val arquivo = planilha(
            cabecalho,
            listOf(
                listOf(1, "2025-01-01", 5, 100.00),
                listOf(1, "2025-01-02", 3, 60.00),
            ),
        )

        val resposta = service.importar(arquivo)

        assertEquals(2, resposta.importados)
        assertEquals(2, resposta.diasDeHistorico)
        assertTrue(resposta.erros.isEmpty())
        assertTrue(resposta.avisos.any { it.contains("90") })
    }

    @Test
    fun `rejeita arquivo que nao e xlsx`() {
        val arquivo = MockMultipartFile("arquivo", "vendas.csv", "text/csv", "conteudo".toByteArray())

        assertFailsWith<ImportacaoException> { service.importar(arquivo) }
    }
}
