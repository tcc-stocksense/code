---
tags: [conceito, arquitetura]
atualizado: 2026-07-13
fonte: ../docs/frontend.md
---

# Stack e arquitetura do frontend

## Decisão de stack
**HTML/CSS/JavaScript vanilla**, sem framework e sem build tooling. Confirmado no C4 e no `docs/frontend.md`.
- **Sem React/Vue, sem webpack/vite.** (React aparece **só** no `../prototype/`, que é referência visual — não é o sistema.)
- **MPA (multi-página):** cada tela é um `.html` independente; sem roteador client-side. Isola o trabalho (cada colega dono da sua tela).
- **ES Modules nativos:** `import`/`export` via `<script type="module">`. Sem bundler.
- **Chart.js via CDN** — única lib externa, só para gráficos.

## Estrutura de pastas (`web/`)
```
web/
├── index.html          → redireciona p/ dashboard ou login
├── pages/*.html        → uma tela = um HTML
├── js/
│   ├── core/           → FUNDAÇÃO (config, apiClient, auth, format, mock)
│   ├── components/     → UI reutilizável (layout, kpiCard, charts, modal, toast…)
│   └── pages/*.page.js → controlador de cada tela
├── css/                → tokens, base, components, pages/
└── serve.json          → config do `npx serve` (ver [[camada-mock-e-api]])
```

## Regra de ouro
Ninguém edita `core/` ou `components/` durante o desenvolvimento de uma tela — só consome. São a **fundação estável** (assinaturas em `docs/frontend.md §3`).

## Fundação `core/`
- `config.js` — `API_BASE_URL` (única URL de API do sistema).
- `apiClient.js` — `apiGet/Post/Patch/Upload`, header de auth automático, erro RFC 7807. Ver [[camada-mock-e-api]].
- `auth.js` — `login/requireAuth/logout/getToken`.
- `format.js` — `moedaBR/dataBR/numero` (padrão BR).

## Convenções
- Arquivos `kebab-case`; funções `camelCase`.
- Datas exibidas em `DD/MM/AAAA`, enviadas à API em ISO.
- **Nenhum `fetch` fora do `apiClient`; nenhuma URL de API fora do `config.js`.** ✅ auditado.
- Toda `page.js` protegida começa com `requireAuth()`.

Relacionado: [[estados-de-ui]] · [[integracao-backend]] · [[overview]]
