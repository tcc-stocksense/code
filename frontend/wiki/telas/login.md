---
tags: [tela, mvp]
endpoint: POST /auth/login
prioridade: MVP
status_integracao: a-validar
atualizado: 2026-07-13
---

# Tela — Login

**Objetivo:** autenticar no estabelecimento e entrar no sistema.

**Endpoint:** `POST /auth/login` (via `auth.login()`, guarda token no `sessionStorage`).

**Comportamento:** form email+senha (pré-preenchido em dev), spinner no submit, sucesso → `dashboard.html`, erro → `toast.erro`. Tem o botão de toggle de mock. "Esqueci minha senha" sem ação.

**Estados:** loading (spinner) ✓ · erro ✓ · (vazio n/a).

**Integração:** ao reativar auth, o token JWT do backend passa a valer; `requireAuth()` (hoje no-op) volta a proteger as demais telas. Ver [[camada-mock-e-api]] e [[decisoes]] (D5).

Relacionado: [[overview]]
