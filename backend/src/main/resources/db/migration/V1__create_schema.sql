CREATE TABLE estabelecimento (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nome_fantasia VARCHAR(100) NOT NULL,
    cnpj          VARCHAR(18),
    endereco      VARCHAR(200)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE produto (
    produto_id             INT PRIMARY KEY,
    nome                   VARCHAR(100)   NOT NULL,
    estoque_atual          INT            NOT NULL,
    categoria              VARCHAR(50),
    unidade_medida         VARCHAR(10),
    preco_custo            DECIMAL(10, 2),
    preco_venda            DECIMAL(10, 2),
    nivel_servico_alvo     DECIMAL(5, 2)  DEFAULT 0.95,
    -- campos calculados pelo motor preditivo --
    classe_abc             CHAR(1),
    desvio_padrao_demanda  DECIMAL(10, 4),
    ponto_reposicao        DECIMAL(10, 2),
    estoque_seguranca      DECIMAL(10, 2),
    data_ultimo_calculo    DATETIME
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE fornecedor (
    fornecedor_id INT PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    contato       VARCHAR(50)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE produto_fornecedor (
    produto_id              INT           NOT NULL,
    fornecedor_id           INT           NOT NULL,
    lead_time_medio         INT           DEFAULT 3,
    variabilidade_lead_time DECIMAL(10, 4) DEFAULT 1.0,
    PRIMARY KEY (produto_id, fornecedor_id),
    CONSTRAINT fk_pf_produto    FOREIGN KEY (produto_id)    REFERENCES produto    (produto_id),
    CONSTRAINT fk_pf_fornecedor FOREIGN KEY (fornecedor_id) REFERENCES fornecedor (fornecedor_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE venda (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    produto_id     INT            NOT NULL,
    data_hora      DATETIME       NOT NULL,
    quantidade     INT            NOT NULL,
    valor_venda    DECIMAL(10, 2),
    is_promocional SMALLINT       DEFAULT 0,
    CONSTRAINT fk_venda_produto FOREIGN KEY (produto_id) REFERENCES produto (produto_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE previsao (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    produto_id          INT            NOT NULL,
    data_previsao       DATE           NOT NULL,
    quantidade_prevista DECIMAL(10, 2),
    modelo_utilizado    VARCHAR(50),
    mape                DECIMAL(8, 4),
    rmse                DECIMAL(10, 4),
    mae                 DECIMAL(10, 4),
    executado_em        DATETIME,
    CONSTRAINT fk_previsao_produto FOREIGN KEY (produto_id) REFERENCES produto (produto_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE perda_estoque (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT         NOT NULL,
    quantidade INT         NOT NULL,
    motivo     VARCHAR(50),
    data_perda DATE        NOT NULL,
    CONSTRAINT fk_perda_produto FOREIGN KEY (produto_id) REFERENCES produto (produto_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
