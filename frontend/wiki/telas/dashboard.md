---
tags: [tela, mvp]
endpoint: GET /dashboard
prioridade: MVP
status_integracao: a-validar
atualizado: 2026-07-13
---

# Tela — Dashboard (Home)

**Objetivo:** panorama diário — o que precisa de atenção agora.

**Endpoint:** `GET /dashboard`.

**Conteúdo:**
- **Banner de alerta** (N em risco / M críticos) → link para [[alertas]].
- **4 KPIs:** risco em 7 dias · crítico agora (`<3`) · valor em risco (coef. ABRAS 0,07÷4 — ⚠️ confirmar com back) · acurácia (`100 − MAPE Prophet`).
- **Gráfico** de faturamento (histórico + projeção) — Chart.js linha.
- **Tabela "próximos alertas"** (top 5 por urgência) → linha/botão vão para [[produto-detalhe]].

**Estados:** loading ✓ · vazio ✓ · erro ✓ (ver [[estados-de-ui]]).

**Integração:** projeção deve vir do motor real (não seno+ruído); confirmar regra do "valor em risco". Ver [[integracao-backend]] e [[inteligencia-de-reposicao]].

Relacionado: [[alertas]] · [[produto-detalhe]] · [[overview]]
