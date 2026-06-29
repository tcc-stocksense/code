-- =====================================================================
-- StockSense — Schema inicial (MySQL 8.0)
-- Consolida o que antes eram V1..V4. A partir daqui, NUNCA editar:
-- toda alteração futura entra como V2__, V3__, ... (regra do CLAUDE.md backend §6).
--
-- Decisões refletidas aqui:
--   * Login no nível do estabelecimento (email + senha_hash) — sem tabela usuario no MVP.
--   * estabelecimento_id de fábrica em produto (preparação multi-estabelecimento).
--   * previsao guarda apenas os pontos diários; métricas dos modelos vão para metrica_modelo.
--   * metrica_modelo: 2 linhas por execução (Holt-Winters e Prophet) — alimenta a Tela 10.
--   * perda_estoque REMOVIDA (módulo ESG fora do escopo).
--   * ON DELETE explícito em todas as FKs (mestre/histórico = RESTRICT; derivado/elo = CASCADE).
--   * Índices que antes estavam no V4 agora são inline.
-- =====================================================================

-- ---------------------------------------------------------------------
-- estabelecimento — também guarda a credencial de acesso (login do MVP)
-- ---------------------------------------------------------------------
CREATE TABLE estabelecimento (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nome_fantasia VARCHAR(100) NOT NULL,
    cnpj          VARCHAR(18),
    endereco      VARCHAR(200),
    email         VARCHAR(100) NOT NULL,
    senha_hash    VARCHAR(255) NOT NULL,        -- bcrypt/argon2 (gerado pelo backend)
    CONSTRAINT uq_estabelecimento_email UNIQUE (email)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- produto — produto_id é chave natural definida pelo gestor (ver Guia de Importação)
-- ---------------------------------------------------------------------
CREATE TABLE produto (
    produto_id             INT PRIMARY KEY,
    estabelecimento_id     INT            NOT NULL DEFAULT 1,
    nome                   VARCHAR(100)   NOT NULL,
    estoque_atual          INT            NOT NULL,
    categoria              VARCHAR(50),
    unidade_medida         VARCHAR(10),
    preco_custo            DECIMAL(10, 2),
    preco_venda            DECIMAL(10, 2),
    nivel_servico_alvo     DECIMAL(5, 2)  DEFAULT 0.95,
    -- campos calculados pelo motor preditivo — nunca recebidos via planilha --
    classe_abc             CHAR(1),
    desvio_padrao_demanda  DECIMAL(10, 4),
    ponto_reposicao        DECIMAL(10, 2),
    estoque_seguranca      DECIMAL(10, 2),
    data_ultimo_calculo    DATETIME,
    CONSTRAINT fk_produto_estabelecimento
        FOREIGN KEY (estabelecimento_id) REFERENCES estabelecimento (id)
        ON DELETE RESTRICT
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- fornecedor
-- ---------------------------------------------------------------------
CREATE TABLE fornecedor (
    fornecedor_id INT PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    contato       VARCHAR(50)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- produto_fornecedor — lead time real por produto/fornecedor (N:N)
-- ---------------------------------------------------------------------
CREATE TABLE produto_fornecedor (
    produto_id              INT            NOT NULL,
    fornecedor_id           INT            NOT NULL,
    lead_time_medio         INT            DEFAULT 3,
    variabilidade_lead_time DECIMAL(10, 4) DEFAULT 1.0,
    PRIMARY KEY (produto_id, fornecedor_id),
    CONSTRAINT fk_pf_produto
        FOREIGN KEY (produto_id) REFERENCES produto (produto_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pf_fornecedor
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedor (fornecedor_id)
        ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- venda — histórico (planilha 5; mínimo 90 dias). Dado de histórico => RESTRICT.
-- ---------------------------------------------------------------------
CREATE TABLE venda (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    produto_id     INT            NOT NULL,
    data_hora      DATETIME       NOT NULL,
    quantidade     INT            NOT NULL,
    valor_venda    DECIMAL(10, 2),
    is_promocional SMALLINT       DEFAULT 0,
    CONSTRAINT fk_venda_produto
        FOREIGN KEY (produto_id) REFERENCES produto (produto_id)
        ON DELETE RESTRICT,
    INDEX idx_venda_produto_data (produto_id, data_hora)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- previsao — APENAS os pontos diários da projeção (30 linhas por execução).
-- O motor mensal acumula (append): a "rodada atual" é o maior executado_em.
-- ---------------------------------------------------------------------
CREATE TABLE previsao (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    produto_id          INT            NOT NULL,
    data_previsao       DATE           NOT NULL,
    quantidade_prevista DECIMAL(10, 2),
    modelo_utilizado    VARCHAR(50),               -- vencedor (denormalizado p/ o gráfico)
    executado_em        DATETIME       NOT NULL,
    CONSTRAINT fk_previsao_produto
        FOREIGN KEY (produto_id) REFERENCES produto (produto_id)
        ON DELETE CASCADE,
    INDEX idx_previsao_produto_exec (produto_id, executado_em),
    INDEX idx_previsao_produto_data (produto_id, data_previsao)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- metrica_modelo — 2 linhas por execução (Holt-Winters e Prophet).
-- Fonte da Tela 10 (comparativo) e do KPI de acurácia do dashboard.
-- ---------------------------------------------------------------------
CREATE TABLE metrica_modelo (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    produto_id   INT          NOT NULL,
    modelo       VARCHAR(50)  NOT NULL,            -- 'holt_winters' | 'prophet'
    mape         DECIMAL(8, 4),
    rmse         DECIMAL(10, 4),
    mae          DECIMAL(10, 4),
    selecionado  BOOLEAN      NOT NULL DEFAULT FALSE,
    executado_em DATETIME     NOT NULL,
    CONSTRAINT fk_metrica_produto
        FOREIGN KEY (produto_id) REFERENCES produto (produto_id)
        ON DELETE CASCADE,
    CONSTRAINT uq_metrica UNIQUE (produto_id, modelo, executado_em),
    INDEX idx_metrica_produto_exec (produto_id, executado_em)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
