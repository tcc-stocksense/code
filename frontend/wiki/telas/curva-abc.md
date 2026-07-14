---
tags: [tela, mvp]
endpoint: GET /curva-abc
prioridade: MVP
status_integracao: a-validar
atualizado: 2026-07-13
---

# Tela — Curva ABC

**Objetivo:** priorizar produtos por faturamento (análise de Pareto).

**Endpoint:** `GET /curva-abc?periodo=` (o front **envia o período** — deve recalcular via API, ≠ protótipo).

**Conteúdo:** gráfico de Pareto (top-30 por faturamento, cor por classe) + linha de % acumulado e referência 80%; 3 cards A/B/C (contagem + % do faturamento + prioridade); tabela com % acumulada.

**Estados:** loading ✓ · vazio ✓ · erro ✓.

**Integração:** classificação ABC é **calculada no backend** (ranking relativo entre todos os produtos). O filtro de período deve recalcular no servidor. Ver [[modelo-de-dados]] e [[integracao-backend]].

Relacionado: [[overview]]
