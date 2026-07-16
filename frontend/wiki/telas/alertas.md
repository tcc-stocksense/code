---
tags: [tela, mvp]
endpoint: GET /alertas
prioridade: MVP
status_integracao: a-validar
atualizado: 2026-07-13
---

# Tela — Alertas de reposição

**Objetivo:** listar o que precisa ser pedido, por urgência.

**Endpoint:** `GET /alertas` (produtos com `diasRuptura ≤ 7`, ordenados).

**Conteúdo:** por produto — estoque atual, "vai faltar em N dias" (ou "já zerou"), lead time, "pedir X un" (`demandaMedia × (leadTime+7)`), fornecedor. Ações: "Detalhe" → [[produto-detalhe]]; "Marcar como pedido" (toggle local, não persiste). Botão "Gerar relatório" → [[sugestao-compra]].

**Estados:** loading ✓ · vazio ✓ ("nenhum produto precisa ser pedido") · erro ✓.

**Integração:** regra `≤ 7` e `qtdSugerida` vêm da [[inteligencia-de-reposicao]] — alinhar corte com o backend. "Marcar como pedido" pode virar persistência futura.

Relacionado: [[sugestao-compra]] · [[dashboard]] · [[overview]]
