---
tags: [tela, pos-mvp]
endpoint: GET /sugestao-compra
prioridade: Pós-MVP
status_integracao: a-validar
atualizado: 2026-07-13
---

# Tela — Sugestão de compra

**Objetivo:** montar o pedido de compra, agrupado por fornecedor.

**Endpoint:** `GET /sugestao-compra` (produtos que `precisaPedir`, agrupados por fornecedor).

**Conteúdo:** card de resumo (total dos itens marcados); por fornecedor — itens com checkbox, **quantidade editável** (recalcula subtotal ao vivo), preço e subtotal. Botões PDF/WhatsApp/Salvar/Confirmar sem ação (Pós-MVP).

**Estados:** loading ✓ · vazio ✓ · erro ✓.

**Integração:** `qtdSugerida` vem da [[inteligencia-de-reposicao]]. PDF/WhatsApp e persistência de pedido são Pós-MVP. Chega-se aqui também por [[alertas]].

Relacionado: [[alertas]] · [[overview]]
