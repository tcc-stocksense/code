---
tags: [decisoes, adr]
atualizado: 2026-07-13
---

# Decisões (ADRs)

Registro de decisões relevantes ao frontend. Cada uma: contexto → decisão → status.

## D1 — Stack vanilla, sem framework
**Contexto:** C4 define frontend HTML/CSS/JS puro. **Decisão:** MPA, ES Modules, Chart.js via CDN; sem React/Vue/bundler. **Status:** firme. React só no `../prototype/` (referência). Ver [[stack-e-arquitetura]].

## D2 — Mock-first
**Contexto:** frontend precisa evoluir sem depender do backend. **Decisão:** camada de mock ligada por padrão, com o `fetch` real já pronto atrás de um flag. **Status:** ativo; desligar na [[integracao-backend]]. Ver [[camada-mock-e-api]].

## D3 — Pasta `frontend-sistema/` no repo
**Contexto:** o repo `tcc-stocksense/code` já tinha uma pasta `frontend/` (esqueleto). **Decisão:** publicar nossa v1 em **`frontend-sistema/`** (separada), direto na `main`. **Status:** feito. **Pendência:** decidir com o grupo se consolida em `frontend/` no futuro. Ver [[integracao-backend]].

## D4 — Cor de marca (verde × azul) — ABERTA ⚠️
**Contexto:** o protótipo usa **verde**; o `docs/frontend.md` especifica **azul** (`--cor-primaria: #1f4e8c`). **Decisão:** pendente — divergência a resolver antes de fechar o visual. **Status:** ABERTA. Fonte: `docs/analise-aderencia.md`.

## D5 — `requireAuth()` desativado temporariamente
**Contexto:** sem backend/JWT, exigir login travaria a navegação de QA. **Decisão:** `requireAuth()` é no-op (comentado) até o backend existir. **Status:** reativar na [[integracao-backend]].

## D6 — Modelo de reposição no mock
**Contexto:** protótipo não calculava ponto de reposição/estoque de segurança. **Decisão:** implementar as fórmulas clássicas no mock como fonte única, expor via `PATCH /produtos/{id}/parametros`. **Status:** feito; avaliar migração p/ backend. Ver [[inteligencia-de-reposicao]].

## D7 — Wiki de conhecimento (opcional)
**Contexto:** memória do projeto para integrar com Obsidian, sem confundir o grupo. **Decisão:** layout de repo **padrão** na raiz; wiki num módulo `wiki/` **opcional e auto-contido**. **Status:** feito (esta wiki).
