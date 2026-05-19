package br.com.stocksense.service

import br.com.stocksense.domain.Venda
import br.com.stocksense.dto.response.ErroLinha
import br.com.stocksense.dto.response.VendaImportacaoResponse
import br.com.stocksense.exception.ImportacaoException
import br.com.stocksense.repository.ProdutoRepository
import br.com.stocksense.repository.VendaRepository
import org.apache.poi.ss.usermodel.CellType
import org.apache.poi.ss.usermodel.DateUtil
import org.apache.poi.ss.usermodel.Row
import org.apache.poi.xssf.usermodel.XSSFWorkbook
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.multipart.MultipartFile
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.format.DateTimeFormatter

@Service
class VendaImportacaoService(
    private val vendaRepository: VendaRepository,
    private val produtoRepository: ProdutoRepository,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    companion object {
        private val XLSX_CONTENT_TYPES = setOf(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/octet-stream",
            "application/zip",
        )
        private val DATE_ONLY_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd")
        private val DATE_TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
        private val DATA_MINIMA = LocalDate.of(2000, 1, 1)
        private const val MIN_HISTORICO_DIAS = 90
    }

    private data class VendaValida(
        val produtoId: Int,
        val dataHora: LocalDateTime,
        val quantidade: Int,
        val valorVenda: BigDecimal?,
        val isPromocional: Short,
    )

    @Transactional
    fun importar(file: MultipartFile): VendaImportacaoResponse {
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
            val avisos = mutableListOf<String>()
            val vendasValidas = mutableListOf<VendaValida>()
            var totalLinhas = 0
            var linhasSemValorVenda = 0

            for (rowIndex in 1..sheet.lastRowNum) {
                val row = sheet.getRow(rowIndex) ?: continue
                if (isRowEmpty(row)) continue
                totalLinhas++
                val lineNumber = rowIndex + 1

                val rowErrors = mutableListOf<ErroLinha>()
                val rowAvisos = mutableListOf<String>()

                val venda = parseRow(row, columnMap, lineNumber, rowErrors, rowAvisos)

                erros.addAll(rowErrors)
                avisos.addAll(rowAvisos)

                if (rowErrors.isEmpty() && venda != null) {
                    vendasValidas.add(venda)
                    if (venda.valorVenda == null) linhasSemValorVenda++
                }
            }

            if (linhasSemValorVenda > 0) {
                avisos.add(
                    "$linhasSemValorVenda linha(s) não possuem 'valor_venda'. " +
                        "O cálculo da Curva ABC ficará prejudicado para esses registros.",
                )
            }

            val importados = persistirVendas(vendasValidas)

            val diasDeHistorico = vendasValidas
                .map { it.dataHora.toLocalDate() }
                .toSet()
                .size

            if (diasDeHistorico in 1 until MIN_HISTORICO_DIAS) {
                avisos.add(
                    "Histórico importado contém $diasDeHistorico dias. " +
                        "O mínimo recomendado para previsões confiáveis é $MIN_HISTORICO_DIAS dias. " +
                        "Os modelos preditivos podem ter acurácia reduzida.",
                )
            }

            log.info(
                "Importação de vendas concluída: {} linhas processadas, {} importadas, {} dias de histórico, {} avisos",
                totalLinhas, importados, diasDeHistorico, avisos.size,
            )

            return VendaImportacaoResponse(totalLinhas, importados, diasDeHistorico, erros, avisos)
        }
    }

    private fun persistirVendas(vendas: List<VendaValida>): Int {
        if (vendas.isEmpty()) return 0

        val minDate = vendas.minOf { it.dataHora.toLocalDate() }.atStartOfDay()
        val maxDate = vendas.maxOf { it.dataHora.toLocalDate() }.atTime(LocalTime.MAX)

        for (produtoId in vendas.map { it.produtoId }.toSet()) {
            val deletados = vendaRepository.deleteByProdutoIdAndDataHoraBetween(produtoId, minDate, maxDate)
            if (deletados > 0) {
                log.info(
                    "Deduplicação: {} venda(s) removida(s) para produto {} no período [{}, {}]",
                    deletados, produtoId, minDate.toLocalDate(), maxDate.toLocalDate(),
                )
            }
        }

        vendaRepository.saveAll(vendas.map { v ->
            Venda(
                produtoId = v.produtoId,
                dataHora = v.dataHora,
                quantidade = v.quantidade,
                valorVenda = v.valorVenda,
                isPromocional = v.isPromocional,
            )
        })
        return vendas.size
    }

    private fun parseRow(
        row: Row,
        columnMap: Map<String, Int>,
        lineNumber: Int,
        errors: MutableList<ErroLinha>,
        avisos: MutableList<String>,
    ): VendaValida? {
        // produto_id
        val produtoIdRaw = getCellStringValue(row, columnMap["produto_id"])
        if (produtoIdRaw.isNullOrBlank()) {
            errors.add(ErroLinha(lineNumber, "Campo obrigatório 'produto_id' não foi informado."))
            return null
        }
        val produtoId = parseIntOrNull(produtoIdRaw)
        if (produtoId == null) {
            errors.add(
                ErroLinha(lineNumber, "'produto_id' deve ser um número inteiro. Valor informado: '$produtoIdRaw'."),
            )
            return null
        }
        if (!produtoRepository.existsById(produtoId)) {
            errors.add(
                ErroLinha(
                    lineNumber,
                    "Produto $produtoId não encontrado. Importe o catálogo de produtos antes de importar as vendas.",
                ),
            )
            return null
        }

        // data_hora
        val dataHoraRaw = getCellDateTimeString(row, columnMap["data_hora"])
        if (dataHoraRaw.isNullOrBlank()) {
            errors.add(ErroLinha(lineNumber, "Campo obrigatório 'data_hora' não foi informado."))
            return null
        }
        val dataHora = parseDataHora(dataHoraRaw, lineNumber, errors, avisos) ?: return null

        // quantidade
        val quantidadeRaw = getCellStringValue(row, columnMap["quantidade"])
        if (quantidadeRaw.isNullOrBlank()) {
            errors.add(ErroLinha(lineNumber, "Campo obrigatório 'quantidade' não foi informado."))
            return null
        }
        val quantidade = parseIntOrNull(quantidadeRaw)
        if (quantidade == null || quantidade <= 0) {
            errors.add(
                ErroLinha(
                    lineNumber,
                    "'quantidade' deve ser um número inteiro maior que zero. Valor informado: '$quantidadeRaw'.",
                ),
            )
            return null
        }

        // valor_venda (opcional — null se ausente, null + erro se formato inválido)
        val errosAntesValorVenda = errors.size
        val valorVenda = parseValorVenda(row, columnMap["valor_venda"], lineNumber, errors)
        if (errors.size > errosAntesValorVenda) return null

        // is_promocional (opcional — 0 se ausente, null se valor inválido)
        val isPromocional = parseIsPromocional(row, columnMap["is_promocional"], lineNumber, errors) ?: return null

        return VendaValida(produtoId, dataHora, quantidade, valorVenda, isPromocional)
    }

    private fun parseDataHora(
        raw: String,
        lineNumber: Int,
        errors: MutableList<ErroLinha>,
        avisos: MutableList<String>,
    ): LocalDateTime? {
        val normalized = raw.trim().replace("T", " ")
        val today = LocalDate.now()

        val parsed: LocalDateTime? = when (normalized.length) {
            10 -> runCatching { LocalDate.parse(normalized, DATE_ONLY_FORMATTER).atStartOfDay() }.getOrNull()
            19 -> runCatching { LocalDateTime.parse(normalized, DATE_TIME_FORMATTER) }.getOrNull()
            else -> null
        }

        if (parsed == null) {
            errors.add(
                ErroLinha(
                    lineNumber,
                    "'data_hora' está em formato inválido. Use YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS. Valor informado: '$raw'.",
                ),
            )
            return null
        }

        val date = parsed.toLocalDate()

        if (date.isAfter(today)) {
            errors.add(
                ErroLinha(lineNumber, "'data_hora' não pode ser uma data futura. Valor informado: '$raw'."),
            )
            return null
        }

        if (date.isBefore(DATA_MINIMA)) {
            avisos.add(
                "Linha $lineNumber: 'data_hora' ($raw) é anterior a 2000-01-01. Dado aceito, mas verifique se a data está correta.",
            )
        }

        return parsed
    }

    private fun parseValorVenda(
        row: Row,
        colIndex: Int?,
        lineNumber: Int,
        errors: MutableList<ErroLinha>,
    ): BigDecimal? {
        colIndex ?: return null
        val raw = getCellStringValue(row, colIndex)?.takeIf { it.isNotBlank() } ?: return null

        if (',' in raw) {
            errors.add(
                ErroLinha(
                    lineNumber,
                    "'valor_venda' deve usar ponto como separador decimal (ex: 37.80). Valor informado: '$raw'.",
                ),
            )
            return null
        }
        val value = raw.toBigDecimalOrNull()
        if (value == null || value < BigDecimal.ZERO) {
            errors.add(
                ErroLinha(lineNumber, "'valor_venda' deve ser um número decimal positivo. Valor informado: '$raw'."),
            )
            return null
        }
        return value
    }

    // Retorna null apenas em caso de erro (valor inválido) — ausente/em branco devolve 0 (padrão)
    private fun parseIsPromocional(
        row: Row,
        colIndex: Int?,
        lineNumber: Int,
        errors: MutableList<ErroLinha>,
    ): Short? {
        colIndex ?: return 0.toShort()
        val raw = getCellStringValue(row, colIndex)?.takeIf { it.isNotBlank() } ?: return 0.toShort()

        return when (raw) {
            "0" -> 0.toShort()
            "1" -> 1.toShort()
            else -> {
                errors.add(
                    ErroLinha(lineNumber, "'is_promocional' deve ser 0 ou 1. Valor informado: '$raw'."),
                )
                null
            }
        }
    }

    // Para a coluna data_hora: preserva o componente de hora em células numéricas do Excel
    private fun getCellDateTimeString(row: Row, colIndex: Int?): String? {
        colIndex ?: return null
        val cell = row.getCell(colIndex) ?: return null
        return when (cell.cellType) {
            CellType.STRING -> cell.stringCellValue.trim().ifBlank { null }
            CellType.NUMERIC -> {
                if (DateUtil.isCellDateFormatted(cell)) {
                    val ldt = cell.localDateTimeCellValue
                    if (ldt.toLocalTime() == LocalTime.MIDNIGHT) {
                        ldt.toLocalDate().toString()
                    } else {
                        ldt.format(DATE_TIME_FORMATTER)
                    }
                } else null
            }
            CellType.FORMULA -> {
                when (cell.cachedFormulaResultType) {
                    CellType.STRING -> cell.stringCellValue.trim().ifBlank { null }
                    CellType.NUMERIC -> {
                        if (DateUtil.isCellDateFormatted(cell)) {
                            cell.localDateTimeCellValue.toLocalDate().toString()
                        } else null
                    }
                    else -> null
                }
            }
            else -> null
        }
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
        val missing = listOf("produto_id", "data_hora", "quantidade").filter { it !in columnMap }
        if (missing.isNotEmpty()) {
            throw ImportacaoException(
                "A planilha está faltando as colunas obrigatórias: ${missing.joinToString(", ")}.",
            )
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

    // Aceita "15" e "15.0" (células numéricas exportadas como string); rejeita "15.5"
    private fun parseIntOrNull(value: String): Int? {
        value.toIntOrNull()?.let { return it }
        val d = value.toDoubleOrNull() ?: return null
        val long = d.toLong()
        if (d != long.toDouble() || long < Int.MIN_VALUE || long > Int.MAX_VALUE) return null
        return long.toInt()
    }
}
