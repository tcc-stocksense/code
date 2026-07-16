---
tags: [tela, mvp]
endpoint: GET /produtos, PATCH /produtos/{id}/estoque
prioridade: MVP
status_integracao: a-validar
atualizado: 2026-07-13
---

# Tela — Estoque

**Objetivo:** listar todos os produtos e editar o estoque atual.

**Endpoints:** `GET /produtos` · `PATCH /produtos/{id}/estoque`.

**Conteúdo:** tabela ordenada por urgência (`diasRuptura` crescente), com semáforo, categoria, **estoque editável inline** (stepper − / input / + com confirmar), até-ruptura, badge ABC, botão Detalhe. Filtros combináveis: busca, categoria, status, classe. Clique na linha → [[produto-detalhe]].

**Estados:** loading (skeleton) ✓ · vazio ✓ (sem produtos → ir para [[importar]]) · erro ✓.

**Integração:** o PATCH de estoque já é real (persiste via API). Ao salvar, o backend deve recalcular e devolver `diasRuptura`/status. Paginação hoje é só visual. Ver [[inteligencia-de-reposicao]].

Relacionado: [[produto-detalhe]] · [[alertas]] · [[overview]]
