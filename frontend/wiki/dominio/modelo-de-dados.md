---
tags: [dominio, dados]
atualizado: 2026-07-13
fonte: ../docs/checklist-funcionalidades.md, web/js/core/mock.js
---

# Modelo de dados

Entidades do domínio (PT-BR, conforme convenção do repo). Referência para casar com os DTOs do backend na [[integracao-backend]].

## Produto
Entidade central. Campos usados pelo front:
`id, nome, categoria, estoque, unidade, diasRuptura, classe (A/B/C), precoMedio, demandaMedia, desvioPadrao, cv, tendencia, leadTime, nivelServico, fornecedor, faturamento`.

Campos **derivados** pela [[inteligencia-de-reposicao]] (hoje no mock): `pontoReposicao, estoqueSeguranca, precisaPedir, qtdSugerida`.

Objetos aninhados no detalhe (`GET /produtos/{id}/detalhe`):
- `grafico { labels[], historico[], projecao[] }` — série 90d + projeção 30d.
- `vendasSemana[] { label, total, media }` — últimas 4 semanas.

## Fornecedor
`id, nome, contato, leadTime`. Usado em [[alertas]] e [[sugestao-compra]] (agrupamento por fornecedor).

## Estabelecimento
`nome, cnpj, endereco`. Login é no estabelecimento (sem tabela `usuario` no MVP — decisão do backend). Exibido em [[configuracoes]] e no topbar.

## Usuário
`nome, email, iniciais`. Exibido no avatar/topbar e em [[configuracoes]].

## Classe ABC
`A / B / C` — ranking por faturamento (curva de Pareto). Calculado no backend (ABC é ranking relativo entre todos os produtos). Ver [[curva-abc]].

## ⚠️ Conferir com o backend
Nomes de campos, tipos e **estrutura aninhada** (`grafico`, `vendasSemana`) precisam bater com os DTOs reais — este é o trabalho central da [[integracao-backend]].
