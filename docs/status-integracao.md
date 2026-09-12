# Status da integração front-end ↔ back-end

> Fotografia de **16/08/2026**, depois da rodada de integração descrita abaixo.
> Fonte da verdade do contrato: [`docs/contrato-api-frontend.md`](contrato-api-frontend.md).
> Backlog operacional: [`frontend/docs/tasks-integracao.md`](../frontend/docs/tasks-integracao.md).

## Resumo

O backend expõe **11 endpoints**. Todos os 11 estão consumidos pelo front-end.
Nenhuma linha de código Kotlin foi alterada nesta rodada — o trabalho foi todo do
lado do cliente, reconciliando as telas com o contrato que o backend já publicava.

| | Antes | Depois |
|---|---|---|
| Endpoints do backend ligados | 9 de 11 | **11 de 11** |
| Telas servindo mock sem avisar | 4 | **0** |
| Fallback silencioso para dados fictícios | sim | **não** |

---

## 1. O que foi integrado

### 1.1 Camada de transporte (`web/js/core/`)

| Item | Estado |
|---|---|
| `API_BASE_URL = http://localhost:8080/api` | ✅ |
| JWT `Authorization: Bearer <token>` em toda chamada | ✅ |
| Login real (`POST /api/auth/login`) | ✅ |
| `requireAuth()` ativo nas 9 telas internas | ✅ |
| CORS liberado no backend (`localhost:*`) | ✅ |
| Erros RFC 7807 (`{ status, detail }`) exibidos no toast | ✅ |
| 401/403 limpam a sessão e voltam ao login | ✅ |

**Mudança estrutural — fim do fallback 404 → mock.**
`apiGet/apiPost/apiPatch/apiUpload` capturavam `status === 404` e devolviam dados
fictícios. Isso mascarava três coisas ao mesmo tempo: credencial inválida (o backend
responde 404 no login), rota inexistente e produto inexistente. Agora o mock é uma
escolha explícita do desenvolvedor — botão flutuante → `core/config.js` → `mockAtivo()` —
e qualquer erro da API sobe para a tela.

> O botão de mock também estava mentindo: exibia "Mock ON" por padrão enquanto o
> `apiClient` já falava com a API real. As duas implementações do botão (layout e login)
> foram unificadas em uma só, com `core/config.js` como fonte da verdade.

**Camada de adaptação.** O backend fala `produtoId`, `estoqueAtual`, `unidadeMedida`,
`classeAbc`, `diasAteRuptura`, `demandaMediaDiaria`. As telas falam `id`, `estoque`,
`unidade`, `classe`, `diasRuptura`, `demandaMedia`. A tradução acontece uma vez só, em
`normalizarResposta()` / `normalizarRequisicao()` no `apiClient.js`, em vez de espalhar
`??` por nove páginas.

### 1.2 Endpoints

| # | Endpoint | Tela | Estado |
|---|---|---|---|
| 1 | `POST /api/auth/login` | Login | ✅ ligado |
| 2 | `GET /api/produtos` | Estoque, Alertas, Comparativo | ✅ ligado |
| 3 | `PATCH /api/produtos/{id}/estoque` | Estoque, Detalhe | ✅ **corrigido** |
| 4 | `GET /api/produtos/{id}/detalhe` | Detalhe do produto | ✅ ligado |
| 5 | `GET /api/produtos/{id}/metricas` | Comparativo de modelos | ✅ **ligado agora** |
| 6 | `GET /api/dashboard` | Home | ✅ ligado |
| 7 | `GET /api/alertas` | Alertas, Home | ✅ ligado |
| 8 | `GET /api/curva-abc` | Curva ABC | ✅ ligado |
| 9 | `POST /api/importacao/produtos` | Importar | ✅ ligado |
| 10 | `POST /api/importacao/vendas` | Importar | ✅ ligado |
| 11 | `POST /api/motor/recalcular` | Importar | ✅ ligado |

**#3 — o bug dos 400.** O front enviava `{ estoque: n }`; o `ProdutoEstoqueRequest`
do backend só aceita `{ estoqueAtual: n }`. Três pontos de chamada estavam quebrados
(`estoque.page.js` e duas vezes em `produto-detalhe.page.js`). A tradução do campo
agora acontece no `apiClient`.

**#5 — o endpoint órfão.** Existia pronto no backend e nenhuma linha do front o
chamava: a tela de Comparativo pedia `GET /produtos/metricas` (rota agregada que nunca
existiu), levava 404 e caía no mock. Agora ela itera `GET /produtos/{id}/metricas`
produto a produto, com **limite de 4 requisições simultâneas**, e agrega MAPE/RMSE/MAE
na própria tela, além de exibir o placar de qual modelo o motor selecionou por produto.

### 1.3 Semáforo de reposição

A régua mudou de raiz. Antes o front estimava `diasRuptura` com uma heurística inventada
(`estoque / pontoReposicao × 7`) e coloria por cortes fixos de dias. Agora segue o
contrato: **relativo ao ponto de reposição** calculado pelo motor.

```
🔴 crítico       estoque ≤ PR
🟡 atenção       PR < estoque ≤ PR × 1.5
🟢 ok            estoque > PR × 1.5
⚪ sem cálculo    PR = null (o motor nunca rodou para este produto)
```

O quarto estado é a mudança importante: produto sem previsão não fica verde por
omissão — ele aparece como "sem cálculo", tem filtro próprio na tela de Estoque e
dispara um banner contando quantos produtos estão nessa situação.

### 1.4 Reconciliação por tela

| Tela | O que mudou |
|---|---|
| **Login** | Guarda `estabelecimentoId` e `nomeFantasia` do `LoginResponse` (antes descartava os dois). O `nomeFantasia` alimenta o header. Credencial errada → mensagem única, sem distinguir email de senha. |
| **Home (T2)** | Consome `riscoDeFaltar7Dias`, `criticoAgora`, `mapeMedioModeloSelecionado`. Acurácia = `100 − MAPE`; `null` vira "motor ainda não executado". Gráfico usa `seriesFaturamento` (histórico semanal). Tabela "próximos alertas" sai de `GET /alertas`, top 5. |
| **Estoque (T4)** | Semáforo por PR, coluna "Ponto de reposição" no lugar de "Até ruptura", filtro "sem cálculo", banner quando o motor não rodou. |
| **Detalhe (T6)** | Consome `demandaMediaDiaria`, `desvioPadraoDemanda`, `coeficienteVariacao`, `tendenciaPercentual`, `diasAteRuptura`, `previsoes[]`. Gráfico e tabela vêm da série prevista. Banner quando `previsoes` vem vazio. |
| **Alertas (T5)** | Usa o `semaforo` pronto do backend. "Quanto pedir" = `PR + estoqueSeguranca − estoque`; como o `AlertaResponse` não traz o ES, a página cruza com **uma** chamada a `GET /produtos` (não N). Avisa quando a lista está incompleta por produtos sem PR. |
| **Curva ABC (T7)** | Usa `itens[]` já ordenado, com `percentualDoTotal` e `percentualAcumulado` prontos. `abcProxy: true` exibe a ressalva de ranking por quantidade e troca os rótulos de "Faturamento" para "Quantidade". |
| **Comparativo (T10)** | Reescrita sobre `/produtos/{id}/metricas`. Mostra cobertura ("N de M produtos têm métricas"). |
| **Importar (T3)** | Dois uploads separados, **na ordem** (Vendas fica bloqueada até Produtos ter sucesso), só `.xlsx`. Exibe `importados / totalLinhas`, `diasDeHistorico`, `erros[]` por linha e `avisos[]`. Motor síncrono com aviso de espera e resumo do recálculo. |

### 1.5 Removido por não existir no contrato

| Item | Tela | Motivo |
|---|---|---|
| Card "Valor em risco" | Home | Sem campo no `DashboardResponse` e sem regra de cálculo definida |
| Filtro de período `?periodo=` | Curva ABC | O endpoint aceitava o parâmetro e o ignorava — o filtro era decorativo |
| Coluna "Fornecedor" | Alertas | Sem campo no `AlertaResponse` |
| Planilhas desejáveis (estabelecimento, fornecedores, produto × fornecedor) | Importar | Sem endpoint de importação |
| Projeção de 4 semanas no gráfico | Home | `seriesFaturamento` é só histórico |
| Tabela "vendas por semana" | Detalhe | Sem campo no `ProdutoDetalheResponse` |

### 1.6 Desabilitado com aviso (não apagado)

| Item | Motivo |
|---|---|
| Modal "Editar parâmetros" (lead time, nível de serviço) | `PATCH /api/produtos/{id}/parametros` não existe — pendência P-01 |
| Tela "Sugestão de compra" | `GET /api/sugestao-compra` não existe. Fora do modo mock, a tela explica isso e aponta para Alertas |
| Botões "Marcar como pedido" / "Marcar para pedido" | Sem endpoint de pedidos — marcação é local e o tooltip avisa |

### 1.7 Infra

- **`docker-compose.yml`**: a raiz do nginx apontava para `./frontend`, mas o `index.html`
  está em `frontend/web/`. Subindo por Docker, `http://localhost/` não achava a aplicação.
  Corrigido para `./frontend/web`.
- **`base.css`**: adicionada a classe `.dot-neutral`, usada pelo estado "sem cálculo".

---

## 2. O que falta

### 2.1 Depende do backend (não dá para fazer no front)

| # | O quê | Impacto |
|---|---|---|
| **P-01** | `PATCH /api/produtos/{id}/parametros` — lead time e nível de serviço | Modal de edição desabilitado no Detalhe |
| **P-02** | `GET /api/curva-abc?periodo=` | Curva ABC sempre sobre todo o histórico; filtro escondido |
| **P-03** | Endpoint agregado de métricas | Comparativo faz N chamadas (mitigado com concorrência 4) |
| **P-05** | Motor assíncrono (`202` + `GET /api/motor/status`) | Recálculo trava a tela de Importar enquanto roda |
| **P-06** | Disparo automático do motor pós-importação | O front precisa chamar o motor manualmente |
| — | `GET /api/sugestao-compra` | Tela inteira indisponível fora do mock |
| — | Endpoint de pedidos / reposição marcada | "Marcar como pedido" não persiste |
| — | Campo "valor em risco" no dashboard | Card removido |
| — | Fornecedor no `AlertaResponse` | Coluna removida |

### 2.2 Depende de rodar o sistema

| # | O quê |
|---|---|
| **I-11** | **Teste de fumaça E2E no navegador.** Reproduzir pela UI o fluxo da coleção Postman (`docs/postman/StockSense_E2E.postman_collection.json`): login → importar `2_produtos.xlsx` e `5_vendas.xlsx` → recalcular → conferir T4/T6/T10/T5/T2/T7. Critério: console sem erro; exercitar também o estado **antes** do recálculo, para ver os `null`. |

### 2.3 Decisões em aberto

- **Sugestão de compra em Alertas.** A fórmula adotada foi
  `pontoReposicao + estoqueSeguranca − estoqueAtual`, arredondada para cima. O ES vem de
  uma chamada extra a `GET /produtos`. Se o time preferir outra regra (ex.: cobrir o lead
  time), é um ponto único no código.
- **Faturamento projetado na Home.** O protótipo mostrava 4 semanas de projeção. Como
  `seriesFaturamento` é só histórico, elas foram removidas. A alternativa seria derivá-las
  das `previsoes` do detalhe, produto a produto — caro e fora do MVP.
- **Rótulos do Comparativo.** Assumimos as chaves `holt_winters` e `prophet` como o
  `ml-service` as grava. Se o backend normalizar esses nomes, ajustar `ROTULO`.

---

## 3. Como validar

```bash
# 1. Banco
docker compose up db -d

# 2. Backend (porta 8080)
cd backend && DB_USERNAME=appuser DB_PASSWORD=suasenha ./gradlew bootRun

# 3. ml-service (porta 8000)
cd ml-service && uvicorn main:app --port 8000

# 4. Front-end — servir a pasta frontend/web em qualquer porta local
cd frontend/web && npx serve -l 3000
```

O CORS libera qualquer `http://localhost:*`, então a porta do front não importa.
Credencial de dev (seed): `admin@stocksense.local` / `admin123`.

O botão flutuante no canto inferior direito alterna entre **🟢 API real** e
**🟠 Mock ON**. Se as telas estiverem vazias, confira primeiro se ele está em "API real".

---

## 4. Arquivos alterados nesta rodada

```
backend/src/main/kotlin/br/com/stocksense/config/SecurityConfig.kt   (CORS — já estava pronto, não commitado)
docker-compose.yml                                                    (raiz do nginx)
docs/status-integracao.md                                             (este arquivo)
frontend/docs/tasks-integracao.md                                     (backlog atualizado)
frontend/web/css/base.css                                             (.dot-neutral)
frontend/web/js/core/config.js                                        (flag de mock)
frontend/web/js/core/apiClient.js                                     (transporte + adaptação)
frontend/web/js/core/auth.js                                          (estabelecimentoId, nomeFantasia)
frontend/web/js/components/layout.js                                  (topbar, toggle unificado)
frontend/web/js/components/statusBadge.js                             (semáforo por PR)
frontend/web/js/pages/login.page.js
frontend/web/js/pages/dashboard.page.js
frontend/web/js/pages/estoque.page.js
frontend/web/js/pages/produto-detalhe.page.js
frontend/web/js/pages/alertas.page.js
frontend/web/js/pages/curva-abc.page.js
frontend/web/js/pages/comparativo-modelos.page.js
frontend/web/js/pages/importar.page.js
frontend/web/js/pages/sugestao-compra.page.js
```
