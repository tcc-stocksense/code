# wiki/ — Base de conhecimento do StockSense (opcional)

> **Esta pasta é opcional.** Se você só quer o código, ignore `wiki/` — o projeto (README, `docs/`, `web/`) funciona 100% sem ela. Isto aqui é uma **base de conhecimento** navegável no [Obsidian](https://obsidian.md), que serve de **memória** do projeto: decisões, telas, conceitos e reuniões, tudo interligado.

## O que é

Em vez de reler os documentos crus toda vez, o conhecimento do projeto é **compilado uma vez** em páginas curtas e interligadas, e **mantido atualizado** conforme o projeto evolui. Segue o padrão *LLM Wiki* (um agente escreve/mantém; você navega e pergunta).

Três camadas:

| Camada | Onde | Papel |
|---|---|---|
| **Fontes** (cruas, imutáveis) | `../docs/`, `../design-reference/`, `../prototype/`, `../web/` | A verdade de origem. A wiki referencia, não altera. |
| **Wiki** (esta pasta) | `wiki/` | Páginas sintetizadas e interligadas com `[[links]]`. |
| **Schema** | este README | Convenções de como manter a wiki. |

## Como usar no Obsidian

1. Abra o Obsidian → **"Open folder as vault"** → selecione a pasta **raiz do projeto** (`design_handoff_stocksense/`), não só `wiki/`.
   Assim os `[[links]]` alcançam também as fontes em `docs/`.
2. Comece por [[overview]] ou [[index]].
3. Use o **Graph view** pra ver as conexões.

## Convenções (pra manter o padrão)

- **Páginas curtas e temáticas**, com `[[links]]` para as relacionadas. Nome de arquivo em `kebab-case`.
- **Frontmatter YAML** no topo (`tags`, `status`, `atualizado`) — alimenta o Graph/Dataview.
- [[index]] é o **catálogo** (toda página listada). [[log]] é a **linha do tempo** (append-only).
- Ao aprender algo novo (reunião, decisão, contrato de API), **crie/atualize a página** e registre em [[log]].
- Fontes ficam em `../docs` etc. — **nunca** editar fonte a partir da wiki; a wiki só sintetiza.

## Mapa

- [[overview]] — visão geral do projeto
- [[index]] — catálogo de todas as páginas
- [[log]] — histórico
- `telas/` — as 10 telas · `conceitos/` — arquitetura e regras · `dominio/` — modelo de dados · `decisoes/` — ADRs · `reunioes/` — atas
