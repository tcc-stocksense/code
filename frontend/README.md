# StockSense — Frontend (Sistema de Gestão de Estoque Preditivo)

Sistema web de previsão e gestão de estoque para pequenos mercados/mercadinhos. Cobre login, dashboard, importação de dados, gestão de estoque, alertas de reposição, detalhe de produto, curva ABC, sugestão de compra, configurações e o comparativo técnico de modelos (Holt-Winters × Prophet).

> Faz parte do monorepo **`tcc-stocksense/code`** (backend Kotlin/Spring · ml-service Python/FastAPI · frontend). Esta é a implementação do **frontend**.

## Stack
**HTML / CSS / JavaScript vanilla**, sem framework e sem build tooling. MPA (multi-página), ES Modules nativos, Chart.js via CDN. Consome a API do backend (Spring Boot). O `prototype/` (React) é **só referência visual** — não é o sistema.

## Estrutura

```
.
├── web/                  → o sistema (aplicação vanilla que roda)
├── docs/                 → documentação do frontend
│   ├── frontend.md           arquitetura, telas, contratos de API, estados
│   ├── tasks.md              backlog de execução
│   ├── analise-aderencia.md  decisões pendentes e gaps
│   └── checklist-funcionalidades.md  inventário de tudo que existe
├── prototype/            → protótipo React (referência de design, não é produção)
├── design-reference/     → imagens das telas (design de referência)
└── wiki/                 → base de conhecimento p/ Obsidian (OPCIONAL — ver abaixo)
```

## Como rodar (dev)

```bash
cd web
npx -y serve -l 3000 .
```
Abra `http://localhost:3000`. Roda com **dados mock** por padrão (botão flutuante alterna mock on/off) — não precisa de backend para navegar. Ver `docs/frontend.md §10`.

## Ordem de leitura (para desenvolver)
1. **`docs/analise-aderencia.md`** — decisões pendentes (ex.: cor de marca) e gaps. Alguns são bloqueantes.
2. **`docs/frontend.md`** — arquitetura, fundação (`core/`, `components/`), as 10 telas, contratos de API e os 4 estados obrigatórios.
3. **`docs/tasks.md`** — backlog por pessoa/fase.
4. **`prototype/`** e **`design-reference/`** — referência visual e de comportamento.

## Status
Frontend **v1 funcional** — 10 telas prontas rodando com mock. Próximo passo: **integração com o backend** (ver `docs/frontend.md` e a wiki).

## wiki/ — base de conhecimento (opcional)
A pasta `wiki/` é uma **base de conhecimento navegável no [Obsidian](https://obsidian.md)** (memória do projeto: telas, conceitos, decisões, reuniões, interligados). **É opcional** — quem só quer o código pode ignorá-la. Para usar: abra a **pasta raiz do projeto** como *vault* no Obsidian e comece por `wiki/overview.md`. Detalhes em `wiki/README.md`.
