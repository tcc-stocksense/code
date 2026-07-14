---
tags: [overview]
atualizado: 2026-07-13
---

# StockSense — Visão geral

**StockSense** é um sistema web de **gestão de estoque preditivo** para pequenos mercados/mercadinhos: prevê demanda, aponta o que precisa ser reposto e quando, e dá suporte à decisão de compra. TCC do grupo **tcc-stocksense**.

## Arquitetura macro (monorepo)

Sistema de 3 serviços (ver repo `tcc-stocksense/code`):

| Serviço | Stack | Porta |
|---|---|---|
| Frontend | HTML/CSS/JS vanilla (nginx) | 80 |
| Backend | Kotlin / Spring Boot | 8080 |
| ML Service | Python / FastAPI | 8000 |
| Banco | MySQL 8.0 | 3306 |

> O frontend **nunca** fala com o ML direto — sempre via backend. Ver [[integracao-backend]].

## O frontend (este projeto)

Implementação vanilla, MPA, ES Modules, Chart.js — ver [[stack-e-arquitetura]]. São **10 telas**:

| Tela | Página | Prioridade |
|---|---|---|
| [[login]] | login.html | MVP |
| [[dashboard]] | dashboard.html | MVP |
| [[importar]] | importar.html | MVP |
| [[estoque]] | estoque.html | MVP |
| [[alertas]] | alertas.html | MVP |
| [[produto-detalhe]] | produto-detalhe.html | MVP |
| [[curva-abc]] | curva-abc.html | MVP |
| [[comparativo-modelos]] | comparativo-modelos.html | MVP (núcleo acadêmico) |
| [[sugestao-compra]] | sugestao-compra.html | Pós-MVP |
| [[configuracoes]] | configuracoes.html | Pós-MVP |

## Conceitos-chave

- [[stack-e-arquitetura]] — decisões de stack, estrutura de pastas, fundação `core/`+`components/`.
- [[inteligencia-de-reposicao]] — o "cérebro": estoque de segurança, ponto de reposição, dias até ruptura.
- [[camada-mock-e-api]] — como o front roda sem backend hoje e como liga no real.
- [[estados-de-ui]] — os 4 estados obrigatórios por tela (loading/vazio/erro/sucesso).
- [[integracao-backend]] — o plano de integração e os contratos de API.
- [[modelo-de-dados]] — Produto, Fornecedor, Estabelecimento, Usuário.

## Status atual (2026-07-13)

- Frontend **v1 funcional** — as 10 telas prontas, rodando com dados mock. Publicado no GitHub em `tcc-stocksense/code` na pasta **`frontend-sistema/`** (ver [[decisoes]]).
- Próximo passo: **integração com o backend** (aguardando validação do back numa reunião — ver [[2026-07-13-validacao-backend]]).

Ver [[decisoes]] para o histórico de escolhas e [[log]] para a linha do tempo.
