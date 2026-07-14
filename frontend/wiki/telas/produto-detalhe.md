---
tags: [tela, mvp]
endpoint: GET /produtos/{id}/detalhe, PATCH /produtos/{id}/estoque, PATCH /produtos/{id}/parametros
prioridade: MVP
status_integracao: a-validar
atualizado: 2026-07-13
---

# Tela — Detalhe do produto

**Objetivo:** estatísticas de demanda + decisão de reposição de um produto.

**Endpoints:** `GET /produtos/{id}/detalhe` · `PATCH /produtos/{id}/estoque` · `PATCH /produtos/{id}/parametros`.

**Conteúdo:**
- Gráfico "demanda diária" (90d histórico + 30d projeção).
- 3 KPIs: demanda média/dia · variabilidade (σ + CV%) · tendência.
- **Painel de reposição reativo:** estoque editável, "precisa pedir?", quanto pedir, ponto de reposição, estoque de segurança, dias até ruptura, lead time, nível de serviço. Recalcula ao vivo ao editar estoque ou parâmetros. Ver [[inteligencia-de-reposicao]].
- Modal "Editar parâmetros" (lead time, nível de serviço) → `PATCH /parametros` recalcula tudo.
- Card fornecedor · tabela "vendas por semana".

**Estados:** loading (skeleton) ✓ · não-encontrado 404 ✓ · erro ✓.

**Nota:** acessada a partir de [[estoque]], [[alertas]] e [[dashboard]] via `?id=`. Depende do rewrite no `serve.json` para preservar a query (ver [[camada-mock-e-api]]).

**Integração:** shape aninhado (`grafico`, `vendasSemana`) e campos derivados precisam casar com o back. Ver [[modelo-de-dados]].

Relacionado: [[estoque]] · [[inteligencia-de-reposicao]] · [[overview]]
