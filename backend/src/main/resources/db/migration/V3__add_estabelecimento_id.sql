ALTER TABLE produto
    ADD COLUMN estabelecimento_id INT NOT NULL DEFAULT 1
        AFTER produto_id,
    ADD CONSTRAINT fk_produto_estabelecimento
        FOREIGN KEY (estabelecimento_id) REFERENCES estabelecimento (id);
