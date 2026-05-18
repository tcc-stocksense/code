CREATE INDEX idx_venda_produto_data     ON venda         (produto_id, data_hora);
CREATE INDEX idx_previsao_produto_data  ON previsao      (produto_id, data_previsao);
CREATE INDEX idx_perda_produto_data     ON perda_estoque (produto_id, data_perda);
