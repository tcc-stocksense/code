# CLAUDE.md — StockSense (frontend)

Frontend **vanilla** (HTML/CSS/JS, MPA, ES Modules, Chart.js) do **StockSense** — sistema web de gestão de estoque preditivo para pequenos mercados. Parte do monorepo `tcc-stocksense/code` (backend Kotlin/Spring · ml-service Python/FastAPI).

## Leia o contexto antes de começar
Este projeto tem uma **base de conhecimento** em `wiki/` (vault Obsidian). Para se orientar rápido, comece por:
1. **`wiki/overview.md`** — visão geral, as 10 telas, status atual.
2. **`wiki/index.md`** — catálogo de todas as páginas.
3. **`wiki/conceitos/integracao-backend.md`** — plano e contratos da integração (foco atual).

**Contrato de API (fonte da verdade):** `../docs/contrato-api-frontend.md` (raiz do monorepo) —
rotas, shapes JSON reais e divergências validadas contra o backend. As tarefas da integração
estão em `docs/tasks-integracao.md`. Em caso de conflito com o wiki ou com `backend/CLAUDE.md`,
o contrato prevalece.

**Mantenha o conhecimento vivo:** ao decidir/aprender algo (reunião, contrato de API, decisão), atualize a página relevante em `wiki/` e registre uma linha em `wiki/log.md`. Ver `wiki/README.md` para as convenções.

## Estrutura
- `web/` — a aplicação. Rodar: `cd web && npx -y serve -l 3000 .` (mock ligado por padrão; não precisa de backend).
- `docs/` — documentação de handoff (`frontend.md` = arquitetura e contratos de API; fonte da verdade).
- `prototype/` — protótipo React (**referência visual, NÃO é o sistema**).
- `wiki/` — base de conhecimento (opcional; ver `wiki/README.md`).

## Convenções (resumo — detalhe em `docs/frontend.md`)
- Vanilla, sem framework/bundler. **Nenhum `fetch` fora de `web/js/core/apiClient.js`; nenhuma URL de API fora de `web/js/core/config.js`.**
- Mock ligado por padrão; o caminho real de `fetch` já está pronto atrás do flag (`wiki/conceitos/camada-mock-e-api.md`).
- Toda `*.page.js` protegida começa com `requireAuth()` (hoje no-op até o backend/JWT).
- **Prioridade organizacional:** manter layout padrão de repositório; `wiki/` é módulo opcional e não deve virar requisito para quem só mexe no código.
