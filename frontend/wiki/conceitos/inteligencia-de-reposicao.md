---
tags: [conceito, dominio, calculo]
atualizado: 2026-07-13
fonte: web/js/core/mock.js
---

# Inteligência de reposição

O "cérebro" do StockSense: transforma estatística de demanda em **decisão de compra**. Hoje vive no mock (`web/js/core/mock.js`, função `inteligenciaEstoque`); na integração deve migrar para o backend/ML. Ver [[integracao-backend]].

## Fórmulas (gestão de estoque clássica)

| Métrica | Fórmula | Significado |
|---|---|---|
| Estoque de segurança (SS) | `z · σ · √L` | Colchão contra variação da demanda |
| Ponto de reposição (ROP) | `μ · L + SS` | Nível que dispara o pedido |
| Dias até ruptura | `estoque / μ` | Quantos dias até zerar |
| Precisa pedir? | `estoque ≤ ROP` | Gatilho de compra |
| Qtd sugerida | `μ · (L+7) + SS − estoque` | Repor cobrindo lead time + 7 dias |

Onde: **μ** = demanda média/dia · **σ** = desvio-padrão da demanda · **L** = lead time do fornecedor (dias) · **z** = fator de segurança do nível de serviço.

## Fator z por nível de serviço
`80%→0,84 · 85%→1,04 · 90%→1,28 · 95%→1,645 · 97%→1,88 · 98%→2,05 · 99%→2,33`

## Onde aparece
- [[produto-detalhe]] — painel lateral reativo (recalcula ao editar estoque ou parâmetros).
- [[estoque]] — `diasRuptura` recalculado ao editar estoque.
- [[alertas]] / [[sugestao-compra]] — filtram por `precisaPedir` e usam `qtdSugerida`.
- [[dashboard]] — conta produtos em risco / críticos.

## Semáforo de urgência
🔴 crítico `diasRuptura < 3` · 🟡 atenção `3 ≤ dias ≤ 7` · 🟢 ok `dias > 7`. Esses cortes **devem bater com a regra do backend**.

## ⚠️ Ponto de integração
No mock, esses campos são **derivados por fórmula**. Na integração, decidir campo a campo: o **backend calcula e devolve**, ou o front computa? (Ex.: `pontoReposicao`, `estoqueSeguranca`, `tendencia`.) Ver [[integracao-backend]].

Relacionado: [[modelo-de-dados]] · [[comparativo-modelos]]
