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

-- ⚠️ Credencial de DESENVOLVIMENTO LOCAL apenas — email: admin@stocksense.local,
--    senha: admin123 (hash BCrypt abaixo). NUNCA usar este valor em ambiente
--    compartilhado, staging ou produção — trocar por hash gerado no cadastro real.
INSERT IGNORE INTO estabelecimento (id, nome_fantasia, email, senha_hash)
    VALUES (1, 'StockSense Padrão', 'admin@stocksense.local', '$2a$10$ismpcFwGGZWgu9Df1MVmyeE9V00haDVPtIM66rmt2k9SQ9..515K6');

INSERT IGNORE INTO fornecedor (fornecedor_id, nome)
    VALUES (1, 'Fornecedor Padrão');
