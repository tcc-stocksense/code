---
tags: [index]
atualizado: 2026-07-13
---

# Índice — catálogo da wiki

Catálogo de todas as páginas. Atualizar sempre que criar/renomear uma página.

## Núcleo
- [[overview]] — visão geral do projeto
- [[painel-integracao]] — status de integração por tela (Dataview)
- [[log]] — linha do tempo (histórico de ingests/decisões)

## Telas (`telas/`)
- [[login]] — entrar no sistema · `POST /auth/login`
- [[dashboard]] — KPIs + projeção + próximos alertas · `GET /dashboard`
- [[importar]] — upload de planilhas · `POST /importacao` → `POST /motor/recalcular`
- [[estoque]] — listar/editar estoque · `GET /produtos`, `PATCH /produtos/{id}/estoque`
- [[alertas]] — reposição urgente · `GET /alertas`
- [[produto-detalhe]] — estatísticas + reposição · `GET /produtos/{id}/detalhe`
- [[curva-abc]] — Pareto ABC · `GET /curva-abc`
- [[comparativo-modelos]] — HW × Prophet · `GET /metricas`
- [[sugestao-compra]] — compra por fornecedor · `GET /sugestao-compra`
- [[configuracoes]] — preferências · (sem endpoint ligado)

## Conceitos (`conceitos/`)
- [[stack-e-arquitetura]] — stack vanilla, MPA, estrutura de pastas
- [[inteligencia-de-reposicao]] — fórmulas de estoque de segurança/ponto de reposição
- [[camada-mock-e-api]] — mock vs API real, `apiClient`
- [[estados-de-ui]] — loading/vazio/erro/sucesso
- [[integracao-backend]] — plano e contratos de integração

## Domínio (`dominio/`)
- [[modelo-de-dados]] — Produto, Fornecedor, Estabelecimento, Usuário

## Decisões (`decisoes/`)
- [[decisoes]] — ADRs (cor de marca, mock-first, pasta frontend-sistema, etc.)

## Reuniões (`reunioes/`)
- [[2026-07-13-validacao-backend]] — validação do backend (próxima)
- [[_template]] — modelo de ata
