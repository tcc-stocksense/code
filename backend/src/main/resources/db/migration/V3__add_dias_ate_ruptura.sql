-- V3 — Adiciona produto.dias_ate_ruptura (campo calculado pelo motor preditivo).
--
-- O ml-service sempre devolveu dias_ate_ruptura no PredictResponse, mas o backend
-- descartava o valor. Alertas (T5) e dashboard (T2) precisam dele em lote
-- (ordenação por urgência e COUNT <= 7 / < 3), então passa a ser persistido pelo
-- MotorService a cada execução — mesma vida útil de ponto_reposicao e
-- estoque_seguranca. NULL quando o motor ainda não rodou ou a demanda média é zero.

ALTER TABLE produto
    ADD COLUMN dias_ate_ruptura DECIMAL(10, 2) NULL
    AFTER estoque_seguranca;
