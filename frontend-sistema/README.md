# Handoff: StockSense — Sistema de Gestão de Estoque Preditivo

## Overview
Protótipo navegável de um sistema web de previsão e gestão de estoque para pequenos mercados/mercadinhos (StockSense). Cobre login, dashboard, importação de dados, gestão de estoque, alertas de reposição, detalhe de produto, curva ABC, sugestão de compra, configurações e um comparativo técnico de modelos de previsão (Holt-Winters × Prophet).

## About the Design Files
Os arquivos em `prototype/` são **referências de design construídas em HTML/React (JSX)** — mostram a intenção de layout, comportamento e conteúdo, **não são código de produção para copiar diretamente**. Foram feitos como protótipo rápido (React + JSX via Babel no browser, dados mock em memória, tudo roda no cliente).

A tarefa é **recriar este design no ambiente real do projeto**, definido em `frontend.md`: **HTML/CSS/JavaScript vanilla, sem framework**, MPA (multi-page), ES Modules, Chart.js para gráficos. Ou seja: **não portar o JSX** — usar o protótipo como referência visual e de comportamento, e implementar do zero seguindo a arquitetura vanilla do `frontend.md`.

## Fidelity
**Alta fidelidade (hifi)** — cores, tipografia, espaçamento, estados e cálculos do protótipo são a referência final de como o sistema deve se comportar, **exceto** onde `analise-aderencia.md` aponta o contrário (ex.: cor de marca a confirmar, cálculos que devem migrar para o backend).

## Ordem de leitura recomendada (importante)
1. **`analise-aderencia.md`** — leia primeiro. Lista decisões pendentes (stack, cor de marca), lacunas técnicas (contratos de API faltantes, componente `dataTable`) e ajustes nas tarefas. Vários itens são **bloqueantes** e devem ser decididos antes de codar qualquer tela.
2. **`frontend.md`** — arquitetura do front-end: estrutura de pastas, fundação (tokens, componentes, `core/`), as 10 telas, contratos de API esperados, os 4 estados obrigatórios por tela (loading/vazio/erro/sucesso).
3. **`tasks.md`** — backlog de execução, tarefa por tarefa, distribuído por pessoa/fase.
4. **`prototype/`** — o protótipo navegável, para consulta visual e de comportamento durante a implementação de cada tela.

## Screens / Views
As 10 telas (Login, Home/Dashboard, Importar dados, Estoque, Alertas, Detalhe do produto, Curva ABC, Sugestão de compra, Configurações, Comparativo de modelos) estão descritas tela a tela em `frontend.md`. Layout, componentes, cores e conteúdo exato de cada uma podem ser conferidos rodando o protótipo (`prototype/index.html`).

## Interactions & Behavior
Ver `frontend.md` §"Telas" para navegação, e `analise-aderencia.md` para os pontos onde o comportamento do protótipo (cálculo no cliente, simulações) precisa mudar para o sistema real (cálculo no backend, endpoints reais).

## State Management
Ver `frontend.md` para os 4 estados obrigatórios (loading / vazio / erro / sucesso) por tela — **o protótipo não implementa todos eles** (dados eram síncronos); isso é trabalho novo, sinalizado na análise de aderência (item 10).

## Design Tokens
Paleta atual do protótipo (verde) em `prototype/styles.css` (`:root`). **Atenção:** `frontend.md` especifica azul como cor primária — isso é uma divergência a **resolver antes de codar** (ver `analise-aderencia.md` item 2).

## Assets
Ícones: SVGs inline estilo lucide, em `prototype/ui.jsx` (componente `Icon` + variantes). Nenhuma imagem/logo externa usada.

## Files
- `prototype/index.html` — entrada do protótipo (abrir para navegar)
- `prototype/app.jsx` — shell (sidebar, topbar, roteamento por hash)
- `prototype/screens-1.jsx`, `screens-2.jsx`, `screens-3.jsx` — as 10 telas
- `prototype/ui.jsx` — componentes de UI e ícones
- `prototype/data.js` — dados mock e fórmulas de cálculo (ponto de reposição, estoque de segurança, dias até ruptura etc.)
- `prototype/styles.css` — design tokens e estilos atuais
- `frontend.md` — arquitetura do front-end alvo
- `tasks.md` — backlog de execução
- `analise-aderencia.md` — gaps e decisões pendentes entre protótipo e plano
