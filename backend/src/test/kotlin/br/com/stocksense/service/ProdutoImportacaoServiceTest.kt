package br.com.stocksense.service

import br.com.stocksense.domain.Produto
import br.com.stocksense.exception.ImportacaoException
import br.com.stocksense.repository.ProdutoRepository
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

class ProdutoImportacaoServiceTest {

    private val produtoRepository = mockk<ProdutoRepository>()
    private lateinit var service: ProdutoImportacaoService

    @BeforeTest
    fun setUp() {
        service = ProdutoImportacaoService(produtoRepository)
        every { produtoRepository.findByProdutoId(any()) } returns null
        every { produtoRepository.save(any()) } answers { firstArg() }
    }

    private fun planilha(
        headers: List<String>,
        rows: List<List<Any?>>,
        filename: String = "2_produtos.xlsx",
    ): MultipartFile {
        val wb = XSSFWorkbook()
        val sheet = wb.createSheet("produtos")
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

    private val cabecalho = listOf("produto_id", "nome", "estoque_atual", "categoria")

    @Test
    fun `importa planilha valida sem erros`() {
        val arquivo = planilha(
            cabecalho,
            listOf(
                listOf(1, "Arroz Tipo 1 5kg", 40, "Grãos"),
                listOf(2, "Feijão Carioca 1kg", 25, "Grãos"),
            ),
        )

        val resposta = service.importar(arquivo)

        assertEquals(2, resposta.totalLinhas)
        assertEquals(2, resposta.importados)
        assertTrue(resposta.erros.isEmpty())
    }

    @Test
    fun `acusa produto_id duplicado na mesma planilha`() {
        val arquivo = planilha(
            cabecalho,
            listOf(
                listOf(1, "Arroz", 40, "Grãos"),
                listOf(1, "Arroz de novo", 10, "Grãos"),
            ),
        )

        val resposta = service.importar(arquivo)

        assertEquals(1, resposta.importados)
        assertEquals(1, resposta.erros.size)
        assertTrue(resposta.erros.first().mensagem.contains("mais de uma vez"))
    }

    @Test
    fun `rejeita planilha sem coluna obrigatoria`() {
        val arquivo = planilha(
            listOf("produto_id", "nome"), // falta estoque_atual
            listOf(listOf(1, "Arroz")),
        )

        val ex = assertFailsWith<ImportacaoException> { service.importar(arquivo) }
        assertTrue(ex.message!!.contains("estoque_atual"))
    }

    @Test
    fun `acusa estoque_atual negativo na linha`() {
        val arquivo = planilha(
            cabecalho,
            listOf(listOf(1, "Arroz", -5, "Grãos")),
        )

        val resposta = service.importar(arquivo)

        assertEquals(0, resposta.importados)
        assertEquals(1, resposta.erros.size)
        assertTrue(resposta.erros.first().mensagem.contains("estoque_atual"))
    }

    @Test
    fun `rejeita campo calculado preenchido na planilha`() {
        val arquivo = planilha(
            cabecalho + "classe_abc",
            listOf(listOf(1, "Arroz", 40, "Grãos", "A")),
        )

        val resposta = service.importar(arquivo)

        assertEquals(0, resposta.importados)
        assertTrue(resposta.erros.any { it.mensagem.contains("classe_abc") })
    }

    @Test
    fun `rejeita arquivo que nao e xlsx`() {
        val arquivo = MockMultipartFile("arquivo", "dados.txt", "text/plain", "conteudo".toByteArray())

        assertFailsWith<ImportacaoException> { service.importar(arquivo) }
    }
}
