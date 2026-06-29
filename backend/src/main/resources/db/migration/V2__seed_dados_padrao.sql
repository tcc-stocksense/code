-- =====================================================================
-- StockSense — Seed de dados padrão (fallback)
-- DML separada do schema (V1). Usada pelo backend quando o lojista não
-- envia as planilhas desejáveis (1_estabelecimento, 3_fornecedores,
-- 4_produto_fornecedor).
--
-- lead_time_medio = 3 e variabilidade_lead_time = 1.0 já são DEFAULT nas
-- colunas de produto_fornecedor (V1): ao vincular um produto ao Fornecedor
-- Padrão sem especificar esses valores, os defaults entram automaticamente.
--
-- INSERT IGNORE garante idempotência: re-executar não gera erro.
-- =====================================================================

-- ⚠️ SUBSTITUIR senha_hash por um hash REAL (bcrypt/argon2) gerado no backend
--    antes de qualquer uso fora do ambiente de desenvolvimento.
--    O valor abaixo é um PLACEHOLDER inválido de propósito — não autentica.
INSERT IGNORE INTO estabelecimento (id, nome_fantasia, email, senha_hash)
    VALUES (1, 'StockSense Padrão', 'admin@stocksense.local', 'TROCAR_POR_HASH_BCRYPT');

INSERT IGNORE INTO fornecedor (fornecedor_id, nome)
    VALUES (1, 'Fornecedor Padrão');
