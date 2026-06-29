package br.com.stocksense.service

import br.com.stocksense.domain.Produto
import br.com.stocksense.dto.response.ErroLinha
import br.com.stocksense.dto.response.ProdutoImportacaoResponse
import br.com.stocksense.exception.ImportacaoException
import br.com.stocksense.repository.ProdutoRepository
import org.apache.poi.ss.usermodel.Cell
import org.apache.poi.ss.usermodel.CellType
import org.apache.poi.ss.usermodel.DateUtil
import org.apache.poi.ss.usermodel.Row
import org.apache.poi.xssf.usermodel.XSSFWorkbook
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.multipart.MultipartFile
import java.math.BigDecimal

@Service
class ProdutoImportacaoService(
    private val produtoRepository: ProdutoRepository,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    companion object {
        private val CALCULATED_FIELDS = setOf(
            "classe_abc", "desvio_padrao_demanda", "ponto_reposicao",
            "estoque_seguranca", "data_ultimo_calculo",
        )
        private val XLSX_CONTENT_TYPES = setOf(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/octet-stream",
            "application/zip",
        )
    }

    @Transactional
    fun importar(file: MultipartFile): ProdutoImportacaoResponse {
        validateFile(file)

        val workbook = try {
            XSSFWorkbook(file.inputStream)
        } catch (ex: Exception) {
            log.error("Falha ao abrir arquivo xlsx: {}", file.originalFilename, ex)
            throw ImportacaoException("O arquivo enviado está corrompido ou não é um xlsx válido.")
        }

        workbook.use { wb ->
            val sheet = try {
                wb.getSheetAt(0)
            } catch (ex: IllegalArgumentException) {
                throw ImportacaoException("A planilha enviada não contém nenhuma aba.")
            }

            val headerRow = sheet.getRow(0)
                ?: throw ImportacaoException("A planilha não contém linha de cabeçalho.")

            val columnMap = buildColumnMap(headerRow)
            validateRequiredColumns(columnMap)

            val erros = mutableListOf<ErroLinha>()
            var importados = 0
            var totalLinhas = 0
            val seenIds = mutableSetOf<Int>()

            for (rowIndex in 1..sheet.lastRowNum) {
                val row = sheet.getRow(rowIndex) ?: continue
                if (isRowEmpty(row)) continue

                totalLinhas++
                val lineNumber = rowIndex + 1 // número humano: cabeçalho = linha 1

                val rowErrors = processRow(row, columnMap, lineNumber, seenIds)
                if (rowErrors.isEmpty()) {
                    importados++
                } else {
                    erros.addAll(rowErrors)
                }
            }

            log.info(
                "Importação de produtos concluída: {} linhas processadas, {} importados, {} erros",
                totalLinhas, importados, erros.size,
            )
            return ProdutoImportacaoResponse(totalLinhas, importados, erros)
        }
    }

    private fun validateFile(file: MultipartFile) {
        val filename = file.originalFilename?.trim() ?: ""
        if (!filename.lowercase().endsWith(".xlsx")) {
            throw ImportacaoException(
                "Apenas arquivos .xlsx são aceitos. Arquivo recebido: '${filename.ifBlank { "(sem nome)" }}'.",
            )
        }
        val contentType = file.contentType?.lowercase()?.trim() ?: ""
        if (contentType.isNotBlank() && contentType !in XLSX_CONTENT_TYPES) {
            throw ImportacaoException(
                "Tipo de arquivo inválido: '$contentType'. Envie um arquivo .xlsx.",
            )
        }
    }

    private fun buildColumnMap(headerRow: Row): Map<String, Int> {
        val map = mutableMapOf<String, Int>()
        for (cellIndex in 0 until headerRow.lastCellNum) {
            val cell = headerRow.getCell(cellIndex) ?: continue
            val name = cell.stringCellValue.trim().lowercase().replace(" ", "_")
            if (name.isNotBlank()) map[name] = cellIndex
        }
        return map
    }

    private fun validateRequiredColumns(columnMap: Map<String, Int>) {
        val missing = listOf("produto_id", "nome", "estoque_atual").filter { it !in columnMap }
        if (missing.isNotEmpty()) {
            throw ImportacaoException(
                "A planilha está faltando as colunas obrigatórias: ${missing.joinToString(", ")}.",
            )
        }
    }

    private fun processRow(
        row: Row,
        columnMap: Map<String, Int>,
        lineNumber: Int,
        seenIds: MutableSet<Int>,
    ): List<ErroLinha> {
        val errors = mutableListOf<ErroLinha>()

        // Rejeitar campos calculados preenchidos pelo usuário
        for (calcField in CALCULATED_FIELDS) {
            val colIndex = columnMap[calcField] ?: continue
            if (!isCellBlank(row.getCell(colIndex))) {
                errors.add(
                    ErroLinha(
                        lineNumber,
                        "O campo '$calcField' é calculado automaticamente pelo sistema e não deve ser preenchido na planilha.",
                    ),
                )
            }
        }

        // Campos obrigatórios
        val produtoIdRaw = getCellStringValue(row, columnMap["produto_id"])
        val nomeRaw = getCellStringValue(row, columnMap["nome"])
        val estoqueAtualRaw = getCellStringValue(row, columnMap["estoque_atual"])

        if (produtoIdRaw.isNullOrBlank())
            errors.add(ErroLinha(lineNumber, "Campo obrigatório 'produto_id' não foi informado."))
        if (nomeRaw.isNullOrBlank())
            errors.add(ErroLinha(lineNumber, "Campo obrigatório 'nome' não foi informado."))
        if (estoqueAtualRaw.isNullOrBlank())
            errors.add(ErroLinha(lineNumber, "Campo obrigatório 'estoque_atual' não foi informado."))

        if (errors.isNotEmpty()) return errors

        // Validar tipos dos campos obrigatórios
        val produtoId = parseIntOrNull(produtoIdRaw!!)
        if (produtoId == null) {
            errors.add(
                ErroLinha(lineNumber, "'produto_id' deve ser um número inteiro. Valor informado: '$produtoIdRaw'."),
            )
        }

        val estoqueAtual = parseIntOrNull(estoqueAtualRaw!!)
        if (estoqueAtual == null || estoqueAtual < 0) {
            errors.add(
                ErroLinha(
                    lineNumber,
                    "'estoque_atual' deve ser um número inteiro maior ou igual a zero. Valor informado: '$estoqueAtualRaw'.",
                ),
            )
        }

        if (errors.isNotEmpty()) return errors

        // Produto_id duplicado na mesma planilha
        if (!seenIds.add(produtoId!!)) {
            return listOf(
                ErroLinha(lineNumber, "O produto_id '$produtoId' aparece mais de uma vez na planilha."),
            )
        }

        // Validar tamanho dos campos de texto
        val nome = nomeRaw!!.trim()
        if (nome.length > 100) {
            errors.add(ErroLinha(lineNumber, "'nome' deve ter no máximo 100 caracteres."))
        }

        val categoria = getCellStringValue(row, columnMap["categoria"])?.trim()?.takeIf { it.isNotBlank() }
        if (categoria != null && categoria.length > 50) {
            errors.add(ErroLinha(lineNumber, "'categoria' deve ter no máximo 50 caracteres."))
        }

        val unidadeMedida = getCellStringValue(row, columnMap["unidade_medida"])?.trim()?.takeIf { it.isNotBlank() }
        if (unidadeMedida != null && unidadeMedida.length > 10) {
            errors.add(ErroLinha(lineNumber, "'unidade_medida' deve ter no máximo 10 caracteres."))
        }

        // Campos decimais opcionais
        val precoCusto = parseDecimalField(row, columnMap["preco_custo"], "preco_custo", lineNumber, errors)
        val precoVenda = parseDecimalField(row, columnMap["preco_venda"], "preco_venda", lineNumber, errors)
        val nivelServicoAlvo = parseNivelServico(row, columnMap["nivel_servico_alvo"], lineNumber, errors)

        if (errors.isNotEmpty()) return errors

        // Upsert: atualizar se existir, inserir se for novo
        val existing = produtoRepository.findByProdutoId(produtoId)
        if (existing != null) {
            existing.nome = nome
            existing.estoqueAtual = estoqueAtual!!
            existing.categoria = categoria
            existing.unidadeMedida = unidadeMedida
            existing.precoCusto = precoCusto
            existing.precoVenda = precoVenda
            existing.nivelServicoAlvo = nivelServicoAlvo
            produtoRepository.save(existing)
            log.info("Produto {} atualizado via importação de planilha", produtoId)
        } else {
            produtoRepository.save(
                Produto(
                    produtoId = produtoId,
                    nome = nome,
                    estoqueAtual = estoqueAtual!!,
                    categoria = categoria,
                    unidadeMedida = unidadeMedida,
                    precoCusto = precoCusto,
                    precoVenda = precoVenda,
                    nivelServicoAlvo = nivelServicoAlvo,
                ),
            )
            log.info("Produto {} inserido via importação de planilha", produtoId)
        }

        return emptyList()
    }

    private fun parseDecimalField(
        row: Row,
        colIndex: Int?,
        fieldName: String,
        lineNumber: Int,
        errors: MutableList<ErroLinha>,
    ): BigDecimal? {
        colIndex ?: return null
        val raw = getCellStringValue(row, colIndex)?.takeIf { it.isNotBlank() } ?: return null

        if (',' in raw) {
            errors.add(
                ErroLinha(
                    lineNumber,
                    "'$fieldName' deve usar ponto como separador decimal (ex: 12.50). Valor informado: '$raw'.",
                ),
            )
            return null
        }
        val value = raw.toBigDecimalOrNull()
        if (value == null) {
            errors.add(ErroLinha(lineNumber, "'$fieldName' deve ser um número decimal. Valor informado: '$raw'."))
        }
        return value
    }

    private fun parseNivelServico(
        row: Row,
        colIndex: Int?,
        lineNumber: Int,
        errors: MutableList<ErroLinha>,
    ): BigDecimal {
        colIndex ?: return BigDecimal("0.95")
        val raw = getCellStringValue(row, colIndex)?.takeIf { it.isNotBlank() } ?: return BigDecimal("0.95")

        if (',' in raw) {
            errors.add(
                ErroLinha(
                    lineNumber,
                    "'nivel_servico_alvo' deve usar ponto como separador decimal (ex: 0.95). Valor informado: '$raw'.",
                ),
            )
            return BigDecimal("0.95")
        }
        val value = raw.toBigDecimalOrNull()
        if (value == null || value < BigDecimal.ZERO || value > BigDecimal.ONE) {
            errors.add(
                ErroLinha(
                    lineNumber,
                    "'nivel_servico_alvo' deve ser um decimal entre 0.0 e 1.0. Valor informado: '$raw'.",
                ),
            )
            return BigDecimal("0.95")
        }
        return value
    }

    private fun getCellStringValue(row: Row, colIndex: Int?): String? {
        colIndex ?: return null
        val cell = row.getCell(colIndex) ?: return null
        return when (cell.cellType) {
            CellType.STRING -> cell.stringCellValue.trim().ifBlank { null }
            CellType.NUMERIC -> {
                if (DateUtil.isCellDateFormatted(cell)) {
                    cell.localDateTimeCellValue.toLocalDate().toString()
                } else {
                    val num = cell.numericCellValue
                    val long = num.toLong()
                    if (num == long.toDouble()) long.toString() else num.toString()
                }
            }
            CellType.BOOLEAN -> cell.booleanCellValue.toString()
            CellType.FORMULA -> {
                when (cell.cachedFormulaResultType) {
                    CellType.STRING -> cell.stringCellValue.trim().ifBlank { null }
                    CellType.NUMERIC -> {
                        val num = cell.numericCellValue
                        val long = num.toLong()
                        if (num == long.toDouble()) long.toString() else num.toString()
                    }
                    else -> null
                }
            }
            else -> null
        }
    }

    private fun isCellBlank(cell: Cell?): Boolean {
        if (cell == null) return true
        return when (cell.cellType) {
            CellType.BLANK -> true
            CellType.STRING -> cell.stringCellValue.isBlank()
            else -> false
        }
    }

    private fun isRowEmpty(row: Row): Boolean {
        if (row.lastCellNum <= 0) return true
        for (cellIndex in 0 until row.lastCellNum) {
            val cell = row.getCell(cellIndex) ?: continue
            when (cell.cellType) {
                CellType.BLANK -> continue
                CellType.STRING -> if (cell.stringCellValue.isNotBlank()) return false
                else -> return false
            }
        }
        return true
    }

    // Converte string para Int; aceita "1" e "1.0" (células numéricas do Excel), rejeita "1.5"
    private fun parseIntOrNull(value: String): Int? {
        value.toIntOrNull()?.let { return it }
        val d = value.toDoubleOrNull() ?: return null
        val long = d.toLong()
        if (d != long.toDouble() || long < Int.MIN_VALUE || long > Int.MAX_VALUE) return null
        return long.toInt()
    }
}
