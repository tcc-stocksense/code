---
tags: [painel, integracao]
atualizado: 2026-07-13
---

# Painel de integração

Status de integração de cada tela com o backend — **gerado automaticamente** pelo [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) a partir do frontmatter das páginas em `telas/`. Atualiza sozinho quando você muda o campo `status_integracao` de uma tela.

> Requer o plugin **Dataview** habilitado. Sem ele, os blocos abaixo aparecem como texto — ver [[README]] para ativar.

## Status por tela

```dataview
TABLE WITHOUT ID
  file.link AS "Tela",
  prioridade AS "Prioridade",
  status_integracao AS "Status",
  endpoint AS "Endpoint"
FROM "wiki/telas"
SORT status_integracao ASC, prioridade ASC
```

## Contagem por status

```dataview
TABLE WITHOUT ID
  key AS "Status",
  length(rows) AS "Qtd"
FROM "wiki/telas"
GROUP BY status_integracao AS key
SORT key ASC
```

## Pendências abertas (checklist manual)
Ver detalhes em [[integracao-backend]]:
- [ ] Contrato do comparativo: `/metricas` vs `/produtos/{id}/metricas` ([[comparativo-modelos]]).
- [ ] "Valor em risco" (coef. ABRAS) — back ou front? ([[dashboard]]).
- [ ] Campos derivados (`pontoReposicao`, `estoqueSeguranca`, `tendencia`) — back ou front? ([[inteligencia-de-reposicao]]).
- [ ] `dias_ruptura` vindo da API.
- [ ] CORS + JWT (reativar `requireAuth`).

## Legenda de status
- `a-validar` — endpoint existe no mock; falta confirmar/casar com o backend real.
- `divergencia` — contrato do front difere do previsto; alinhar.
- `nao-ligado` — tela não consome API ainda (Pós-MVP).
- `pronto` — integrado e testado (usar quando concluir).

Relacionado: [[integracao-backend]] · [[index]]
