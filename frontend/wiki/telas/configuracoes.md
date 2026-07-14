---
tags: [tela, pos-mvp]
endpoint: (nenhum ligado — PUT /configuracoes/* previsto)
prioridade: Pós-MVP
status_integracao: nao-ligado
atualizado: 2026-07-13
---

# Tela — Configurações

**Objetivo:** preferências do estabelecimento, usuário e notificações.

**Endpoint:** previsto `PUT /configuracoes/*` — **hoje não ligado** (form local, não persiste).

**Conteúdo:** 3 abas — Estabelecimento (nome, CNPJ, endereço), Usuário (nome, email, alterar senha), Notificações (toggle de alerta crítico, resumo por email). Botão "Salvar" mostra "✓ Salvo" mas não persiste.

**Estados:** não busca dados de API hoje (form estático) — ver [[estados-de-ui]].

**Integração (Pós-MVP):** ligar o `PUT /configuracoes/*` para persistir cada aba. Ver [[integracao-backend]].

Relacionado: [[modelo-de-dados]] · [[overview]]
