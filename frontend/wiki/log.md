---
tags: [log]
---

# Log — linha do tempo

Append-only. Cada entrada começa com `## [AAAA-MM-DD] tipo | resumo` (assim `grep "^## \[" log.md` lista tudo).

## [2026-07-14] fix | Endpoint do comparativo alinhado ao padrão
Auditoria do `orientacoes/CLAUDE.md` + task apontou divergência: [[comparativo-modelos]] usava `GET /metricas`. Alterado para `GET /produtos/metricas` (front + mock), alinhando à família `/produtos/…/metricas` do CLAUDE.md e à margem do task S8. Testado (tela renderiza, sem erro de rota). `status_integracao` da tela: `divergencia` → `a-validar`. (Pontos 1 cor-de-marca e 3 requireAuth: mantidos como estão, por decisão do usuário.)

## [2026-07-13] setup | CLAUDE.md + painel Dataview
Criado `CLAUDE.md` na raiz (aponta sessões novas do Claude para a wiki). Criado [[painel-integracao]] com tabela Dataview do status por tela; campo de frontmatter renomeado `status-integracao` → `status_integracao` (compatibilidade Dataview).

## [2026-07-13] setup | Wiki criada
Base de conhecimento inicializada no padrão LLM Wiki. Estrutura: `docs/` (fontes), `wiki/` (conhecimento), layout de repo padronizado (README na raiz). Páginas iniciais: [[overview]], as 10 telas, conceitos ([[stack-e-arquitetura]], [[inteligencia-de-reposicao]], [[camada-mock-e-api]], [[estados-de-ui]], [[integracao-backend]]), [[modelo-de-dados]] e [[decisoes]].

## [2026-07-13] milestone | Frontend v1 funcional publicado
As 10 telas prontas rodando com mock. Publicado no GitHub `tcc-stocksense/code` em `frontend-sistema/` (commit "v1 frontend funcional", direto na main). Ver [[decisoes]].

## [2026-07-13] feature | Tela de detalhe + inteligência de reposição
[[produto-detalhe]] finalizada com painel de reposição **reativo**; modelo de estoque (SS/ROP/dias-ruptura/qtd-sugerida) implementado no mock e exposto via `PATCH /produtos/{id}/parametros`. Ver [[inteligencia-de-reposicao]].

## [2026-07-13] pendente | Aguardando validação do backend
Reunião marcada para validar o back; depois os arquivos do backend entram aqui p/ iniciar a integração. Ver [[integracao-backend]] e [[2026-07-13-validacao-backend]].
