-- Dados de fallback usados pelo backend quando o lojista não envia
-- as planilhas desejáveis (1_estabelecimento, 3_fornecedores, 4_produto_fornecedor).
--
-- lead_time_medio = 3 e variabilidade_lead_time = 1.0 já são os valores DEFAULT
-- declarados nas colunas de produto_fornecedor (V1). Quando o backend vincula
-- um produto ao Fornecedor Padrão sem especificar esses valores, os defaults
-- do schema entram em vigor automaticamente.
--
-- INSERT IGNORE garante idempotência: re-executar esta migration não gera erro.

INSERT IGNORE INTO estabelecimento (id, nome_fantasia)
    VALUES (1, 'StockSense Padrão');

INSERT IGNORE INTO fornecedor (fornecedor_id, nome)
    VALUES (1, 'Fornecedor Padrão');
