---
tags: [tela, mvp, academico]
endpoint: GET /produtos/metricas
prioridade: MVP
status_integracao: a-validar
atualizado: 2026-07-14
---

# Tela — Comparativo de modelos (T10)

**Objetivo:** comparar **Holt-Winters × Prophet** — núcleo acadêmico do TCC (para a banca).

**Endpoint:** `GET /produtos/metricas` — **listagem geral** (agregado + métricas por produto), forma da coleção de `/produtos/{id}/metricas`. Alinhado ao `CLAUDE.md` (família `/produtos/…/metricas`) e à margem do task S8 (*"e/ou listagem geral de métricas"*), já que a tela compara **todos** os produtos e um endpoint por-id não a alimenta sozinho. **Confirmar a rota final com o backend** — ver [[integracao-backend]].

**Conteúdo:** 3 KPIs agregados (MAPE/RMSE/MAE) com badge "melhor"; gráfico de barras agrupadas por produto (select de métrica); tabela detalhada por produto com recomendação; log de execuções (retraining).

**Estados:** loading ✓ · vazio ✓ · erro ✓.

**Integração:** métricas devem ser **reais** de um modelo treinado (hoje são aleatórias a cada carga). Vêm do backend/ML. Ver [[inteligencia-de-reposicao]].

Relacionado: [[overview]] · [[integracao-backend]]
