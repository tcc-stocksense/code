# tasks-integracao.md — Ligar o frontend no backend real

> Backlog **da integração** (mock → API real). Separado do `tasks.md` (construção das telas,
> já concluída sobre o mock). Cada tarefa é autocontida: pode ser dada a uma IA (Claude Code)
> ou a uma pessoa.
>
> **Fonte da verdade do contrato: [`docs/contrato-api-frontend.md`](../../docs/contrato-api-frontend.md)**
> (raiz do monorepo) — rotas, shapes JSON reais, códigos de erro e divergências já validadas
> via Postman. Em caso de conflito com qualquer outro doc (inclusive `backend/CLAUDE.md`),
> o contrato prevalece.
>
> Status: `[ ]` pendente · `[x]` concluído · `[-]` em progresso

## Regras que valem para todas as tarefas

- Nenhum `fetch` fora de `web/js/core/apiClient.js`; nenhuma URL fora de `web/js/core/config.js`.
- Todas as rotas reais têm prefixo **`/api`** e exigem `Authorization: Bearer <token>` (exceto o login).
- Campos calculados pelo motor vêm **`null` até o primeiro recálculo** — toda tela trata esse estado.
- Erros da API são RFC 7807 (`{ status, detail }`) — exibir `detail` no toast.
- Credencial de dev (seed): `admin@stocksense.local` / `admin123`.

---

## FASE I0 — Pré-requisitos (bloqueadores)

- [ ] **I-01 — CORS no backend** `BLOQUEADOR` *(tarefa do backend, registrada aqui para rastreio)*
  O `SecurityConfig` não tem CORS: qualquer chamada do navegador em origem diferente
  (`:3000`/`:80`) falha ao desligar o mock. Pedir ao backend um `CorsConfigurationSource`
  de dev liberando a origem do front. Sem isso, só dá para validar via Postman.

- [ ] **I-02 — `config.js`: base URL real + desligar mock** `MVP`
  `API_BASE_URL = "http://localhost:8080/api"` (atenção ao prefixo `/api`, que o plano antigo
  não tinha) e flag de mock desligado. Manter o mock acessível por flag para dev offline.
  _Depende de: I-01_

- [ ] **I-03 — Auth real (JWT)** `MVP`
  `login()` → `POST /api/auth/login`; guardar `{ token, estabelecimentoId, nomeFantasia }`
  (o response tem os 3 campos — o plano antigo esperava só `token`; `nomeFantasia` alimenta
  o header do layout). `requireAuth()` deixa de ser no-op; `apiClient` injeta o `Authorization`.
  Erro de credencial é **404 com mensagem única** (não distingue email/senha) → toast
  "credenciais inválidas".
  _Depende de: I-02_

---

## FASE I1 — Reconciliação por tela

> Ordem sugerida = ordem do fluxo real de uso. Cada tarefa: apontar a tela para a API real,
> ajustar os campos ao shape do contrato e tratar os estados que o mock não tinha.

- [ ] **I-04 — Tela Importar (S3): dois uploads + motor síncrono** `MVP`
  A maior divergência: **não existe** `POST /api/importacao` único. São
  `POST /api/importacao/produtos` e `POST /api/importacao/vendas` (multipart, campo `arquivo`,
  só `.xlsx`), **nessa ordem**. Depois do sucesso das obrigatórias, chamar
  `POST /api/motor/recalcular` — **síncrono** hoje (Épico 7 suspenso): spinner bloqueante,
  timeout generoso, botão desabilitado, sem retry automático.
  Exibir `erros[]` por linha e `avisos[]` (ex.: histórico < 90 dias **não é erro**).
  Blocos "desejáveis" (estabelecimento/fornecedores) ficam desabilitados — sem endpoint.
  _Depende de: I-03_

- [ ] **I-05 — Tela Estoque (S4)** `MVP`
  `GET /api/produtos` + `PATCH /api/produtos/{id}/estoque` com body `{ "estoqueAtual": n }`.
  Semáforo relativo ao PR (🔴 `estoqueAtual ≤ pontoReposicao`, 🟡 até `×1.5`, 🟢 acima) —
  calcular na tela a partir dos campos do response; sem cortes fixos de dias.
  Tratar `pontoReposicao: null` (motor nunca rodou) como estado "sem cálculo".
  _Depende de: I-03_

- [ ] **I-06 — Tela Detalhe do produto (S6)** `MVP`
  `GET /api/produtos/{id}/detalhe`. Gráfico usa `previsoes[]` (até 30 pontos) do próprio
  response. **Desabilitar/ocultar o modal "Editar parâmetros"** — o
  `PATCH /produtos/{id}/parametros` não existe (pendência P-01). Estados: 404; campos de
  previsão `null` + `previsoes: []` → banner "sem previsão — execute o recálculo".
  _Depende de: I-03_

- [ ] **I-07 — Tela Alertas (S5)** `MVP`
  `GET /api/alertas`. Consumir `semaforo` **pronto do backend** (não recalcular por dias).
  O response **não tem** `fornecedor` nem `quantidadeSugerida`: remover a coluna fornecedor
  do MVP e derivar a sugestão de `pontoReposicao − estoqueAtual + estoqueSeguranca` (buscar
  ES no detalhe) — nunca o `demanda × (leadTime + 7)` do protótipo. Lista vazia ≠ "tudo ok":
  produtos sem PR ficam fora — combinar com o estado do motor.
  _Depende de: I-03_

- [ ] **I-08 — Tela Dashboard (S2)** `MVP`
  `GET /api/dashboard`. **Remover o card "Valor em risco"** (não existe no backend — regra
  indefinida). Acurácia = `100 − mapeMedioModeloSelecionado` (`null` → estado "sem cálculo").
  `seriesFaturamento` é **só histórico** (~8 semanas, `semana` = segunda-feira): o gráfico
  perde as 4 semanas projetadas do protótipo, ou as deriva das `previsoes` do detalhe
  (decisão de tela — documentar a escolha).
  A tabela "próximos alertas" (top 5) vem de `GET /api/alertas` (mesma chamada da S5).
  _Depende de: I-03, I-07_

- [ ] **I-09 — Tela Curva ABC (S7)** `MVP`
  `GET /api/curva-abc` — **sem** `?periodo=` (pendência P-02): esconder/desabilitar o filtro
  de período até existir. `itens[]` já vem ordenado com `percentualAcumulado` pronto (Pareto
  é plot direto). `abcProxy: true` → exibir ressalva "ranking por quantidade (sem valor de
  venda no histórico)".
  _Depende de: I-03_

- [ ] **I-10 — Tela Comparativo de modelos (S8/T10)** `MVP`
  Só existe `GET /api/produtos/{id}/metricas` (**por produto** — a listagem geral do plano
  antigo não existe, pendência P-03). Para a visão agregada: iterar `GET /api/produtos` e
  chamar `/{id}/metricas` por produto (com limite de concorrência, ex. 4 em paralelo).
  Response: 2 linhas (vencedor primeiro, `selecionado: true`); lista vazia = motor nunca
  rodou → estado "rode o motor".
  _Depende de: I-03_

---

## FASE I2 — Validação

- [ ] **I-11 — Teste de fumaça E2E no navegador** `MVP`
  Reproduzir o fluxo da coleção Postman (`docs/postman/StockSense_E2E.postman_collection.json`)
  pela UI: login → importar `2_produtos.xlsx` e `5_vendas.xlsx` (gerados por
  `ml-service/app/tests/generate_synthetic_data.py`) → recalcular → conferir T4/T6/T10/T5/T2/T7.
  Critério: sem erro no console; todos os estados vazios/erro exercitados (testar também
  **antes** do recálculo para ver os `null`).
  _Depende de: I-04 … I-10_

---

## Pendências com o backend (negociar, não implementar no front)

| # | O quê | Impacto no front | Rastreio |
|---|---|---|---|
| P-01 | `PATCH /api/produtos/{id}/parametros` (lead time, nível de serviço) | Modal da T6 desabilitado | Task nova no `backend/tasks.md` |
| P-02 | `GET /api/curva-abc?periodo=` | Filtro de período da T7 escondido | Task nova no backend |
| P-03 | Endpoint agregado de métricas (ou manter iteração por produto) | T10 itera N chamadas | Decidir com o time |
| P-04 | CORS de dev (I-01) | **Bloqueia toda a integração no navegador** | `SecurityConfig` |
| P-05 | Motor assíncrono (202 + `GET /api/motor/status`) | Fase 1.5 do `tasks.md` (suspensa) | Épico 7 do backend |
| P-06 | Disparo automático do motor pós-importação (T-44) | Enquanto não existir, o front chama o motor | Épico 7 do backend |

---

*Atualizar o status (`[ ]` → `[x]`) conforme as tarefas forem concluídas; registrar decisões novas no contrato (`docs/contrato-api-frontend.md`) e, se usar o wiki, em `wiki/conceitos/integracao-backend.md`.*
