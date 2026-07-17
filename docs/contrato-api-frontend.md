# Contrato API → Telas — Guia de Integração do Frontend

> **StockSense · TCC 2026** — Relatório de handoff backend → frontend.
> Gerado a partir dos controllers e DTOs reais da `main` (Épicos 1–5 concluídos),
> validados ponta a ponta via Postman (`docs/postman/StockSense_E2E.postman_collection.json`
> é a referência **executável** deste contrato).
>
> Corrige a tabela "a validar" de `frontend/wiki/conceitos/integracao-backend.md` —
> ver [Divergências consolidadas](#divergências-consolidadas) no final.

---

## 1. Regras gerais (valem para todos os endpoints)

- **Base URL:** `http://localhost:8080` (dev). Todas as rotas têm prefixo **`/api`** — o wiki do front lista sem o prefixo; ajustar no `config.js`.
- **Autenticação:** JWT. O único endpoint aberto é `POST /api/auth/login`; **todos os demais** exigem o header `Authorization: Bearer <token>`. Sem token → `401/403`.
- **Multi-tenant implícito:** o `estabelecimentoId` sai do token — nunca é enviado pelo front. Produto de outro estabelecimento responde `404` (não `403`).
- **Formato de erro:** RFC 7807 (`application/problem+json`) em todos os erros:

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Produto 9999 não encontrado."
}
```

- **Datas:** ISO 8601 (`2026-07-15` / `2026-07-15T14:30:00`). Decimais com ponto, serializados como número JSON.
- **Campos calculados pelo motor** (`pontoReposicao`, `estoqueSeguranca`, `diasAteRuptura`, `classeAbc`, `desvioPadraoDemanda`...) vêm **`null` até a primeira execução do motor**. Toda tela deve tratar esse estado (banner "execute o recálculo"), não assumir que existe previsão.
- **⚠️ CORS ainda não está configurado** no backend (`SecurityConfig`). Ao desligar o mock com o front servido em `:3000`/`:80`, o navegador vai bloquear as chamadas. Pendência do backend: adicionar `CorsConfigurationSource` para dev. Até lá, testar via Postman ou servir o front pela mesma origem.
- **Credencial de dev (seed):** `admin@stocksense.local` / `admin123`.

---

## 2. Tabela-resumo: tela → endpoints

| Tela | Endpoint(s) | Status |
|---|---|---|
| T1 Login | `POST /api/auth/login` | ✅ pronto |
| T2 Dashboard | `GET /api/dashboard` | ✅ pronto (sem "valor em risco"; série só histórico) |
| T3 Importação | `POST /api/importacao/produtos` + `POST /api/importacao/vendas` | ✅ pronto (**2 endpoints**, não 1) |
| T3 (pós-importação) | `POST /api/motor/recalcular` | ✅ pronto (**síncrono** — ver §3.4) |
| T4 Estoque | `GET /api/produtos` · `PATCH /api/produtos/{id}/estoque` | ✅ pronto |
| T5 Alertas | `GET /api/alertas` | ✅ pronto |
| T6 Detalhe do produto | `GET /api/produtos/{id}/detalhe` | ✅ pronto (`PATCH .../parametros` **não existe**) |
| T7 Curva ABC | `GET /api/curva-abc` | ✅ pronto (**sem** `?periodo=`) |
| T10 Comparativo de modelos | `GET /api/produtos/{id}/metricas` | ✅ pronto (**por produto**, não listagem geral) |
| T8 Sugestão de compra | `GET /api/sugestao-compra` | ❌ não existe (Pós-MVP) |
| T9 Configurações | `PUT /api/configuracoes/*` | ❌ não existe (Pós-MVP) |
| T1 Reset de senha | `POST /api/auth/reset` | ❌ não existe (Pós-MVP) |

---

## 3. Detalhe por tela

### 3.1 T1 — Login

`POST /api/auth/login` *(único endpoint sem token)*

```json
// Request
{ "email": "admin@stocksense.local", "senha": "admin123" }

// 200 — LoginResponse
{ "token": "eyJhbGciOi...", "estabelecimentoId": 1, "nomeFantasia": "StockSense Padrão" }
```

- `404` para email **ou** senha inválidos — mesma mensagem propositalmente (não vazar qual falhou). O front deve exibir "credenciais inválidas", não "usuário não encontrado".
- `400` com lista de campos quando email/senha em branco.
- Guardar o `token` e enviá-lo em todas as demais chamadas.

### 3.2 T3 — Importação

⚠️ **São dois endpoints separados** (decisão do time), não o `POST /api/importacao` único que o front esperava. Ambos multipart, campo **`arquivo`**, apenas `.xlsx`. **Ordem obrigatória: produtos antes de vendas** (venda de produto inexistente é erro por linha).

`POST /api/importacao/produtos`

```json
// 201 — ProdutoImportacaoResponse
{
  "totalLinhas": 10,
  "importados": 10,
  "erros": [ { "linha": 4, "mensagem": "'estoque_atual' deve ser um número inteiro..." } ]
}
```

`POST /api/importacao/vendas`

```json
// 201 — VendaImportacaoResponse
{
  "totalLinhas": 1703,
  "importados": 1703,
  "diasDeHistorico": 180,
  "erros": [],
  "avisos": [ "Histórico importado contém 45 dias. O mínimo recomendado é 90..." ]
}
```

- Erros **por linha** vão em `erros[]` (a linha é importada = não; as demais seguem). Erros **estruturais** (arquivo não-xlsx, coluna obrigatória faltando) respondem `400` RFC 7807.
- Histórico < 90 dias **não é erro** — vira item em `avisos[]`; a tela deve exibir.
- Reimportar é seguro: produtos fazem upsert por `produto_id`; vendas são deduplicadas por produto no período.
- **Após concluir as importações, o front deve chamar `POST /api/motor/recalcular`** (o disparo automático pós-importação — T-44 — ainda não existe).

### 3.3 T4 — Estoque

`GET /api/produtos`

```json
// 200 — List<ProdutoResponse>
[
  {
    "produtoId": 1,
    "nome": "Arroz 5kg",
    "categoria": "Grãos",
    "unidadeMedida": "un",
    "estoqueAtual": 15,
    "classeAbc": "A",
    "pontoReposicao": 52.52,
    "estoqueSeguranca": 14.85,
    "dataUltimoCalculo": "2026-07-15T21:04:11"
  }
]
```

`PATCH /api/produtos/{id}/estoque`

```json
// Request
{ "estoqueAtual": 55 }

// 200 — ProdutoResponse (o mesmo shape acima, atualizado)
```

- `400` se `estoqueAtual` negativo; `404` se o produto não existe ou é de outro estabelecimento.
- Editar estoque **não** re-roda o motor (decisão registrada): previsão e PR dependem do histórico, não do estoque. O semáforo/dias até ruptura o front recalcula ao re-buscar as telas.
- Semáforo da tabela (T4): relativo ao PR — 🔴 `estoqueAtual ≤ pontoReposicao` · 🟡 até `pontoReposicao × 1.5` · 🟢 acima. Sem cortes fixos de dias.

### 3.4 Motor — recálculo (disparado pela T3 ou botão manual)

`POST /api/motor/recalcular` *(sem body)*

```json
// 200 — MotorRecalculoResponse
{
  "produtosProcessados": 10,
  "produtosComFalha": 0,
  "produtosClassificadosAbc": 10,
  "abcProxy": false,
  "executadoEm": "2026-07-15T21:04:11"
}
```

- ⚠️ **Síncrono hoje** (Épico 7 — async com `202` + `GET /api/motor/status` — está suspenso). Com poucos produtos leva segundos; com centenas pode levar **minutos**. O front deve usar spinner bloqueante + timeout generoso e desabilitar o botão durante a chamada (sem retry automático).
- `produtosComFalha > 0` não é erro HTTP — exibir aviso não-bloqueante ("N produtos não recalculados") e seguir.
- `abcProxy: true` = ranking ABC usou quantidade como proxy (histórico sem `valor_venda`) — exibir a ressalva na T7.
- O "resultado" do motor é o banco atualizado: ao concluir, **re-buscar** `/api/dashboard`, `/api/produtos`, `/api/alertas`, `/api/curva-abc`.
- Quando o Épico 7 for implementado, este endpoint passará a responder `202 { status, statusUrl }` com polling em `GET /api/motor/status` — contrato já congelado, ver `backend/tasks.md` (T-41/T-42).

### 3.5 T6 — Detalhe do produto

`GET /api/produtos/{id}/detalhe`

```json
// 200 — ProdutoDetalheResponse
{
  "produtoId": 1,
  "nome": "Arroz 5kg",
  "categoria": "Grãos",
  "unidadeMedida": "un",
  "estoqueAtual": 15,
  "classeAbc": "A",

  "demandaMediaDiaria": 12.43,
  "desvioPadraoDemanda": 5.4621,
  "coeficienteVariacao": 0.44,
  "tendenciaPercentual": 3.85,

  "pontoReposicao": 52.52,
  "estoqueSeguranca": 14.85,
  "diasAteRuptura": 1.21,
  "dataUltimoCalculo": "2026-07-15T21:04:11",

  "previsoes": [
    { "data": "2026-07-16", "quantidadePrevista": 12.80 },
    { "data": "2026-07-17", "quantidadePrevista": 14.10 }
  ]
}
```

- `previsoes` = série mais recente do motor, até 30 pontos (alimenta o gráfico).
- `demandaMediaDiaria` e `diasAteRuptura` derivam da **previsão** (não do histórico); `tendenciaPercentual` é `null` com menos de 28 dias de venda.
- Motor nunca rodou → campos de previsão `null` e `previsoes: []` — a tela sinaliza "sem previsão", não quebra.
- ⚠️ O `PATCH /api/produtos/{id}/parametros` (modal "Editar parâmetros": lead time, nível de serviço) que o front previa **não existe ainda** — pendência aberta com o backend. Até lá, o modal deve ficar desabilitado ou oculto.

### 3.6 T10 — Comparativo de modelos

`GET /api/produtos/{id}/metricas`

```json
// 200 — List<MetricaResponse> (vencedor primeiro)
[
  { "modelo": "prophet",      "mape": 18.42, "rmse": 4.1123, "mae": 3.2456, "selecionado": true,  "executadoEm": "2026-07-15T21:04:11" },
  { "modelo": "holt_winters", "mape": 22.87, "rmse": 5.0034, "mae": 3.9012, "selecionado": false, "executadoEm": "2026-07-15T21:04:11" }
]
```

- ⚠️ É **por produto** — a listagem geral `GET /api/produtos/metricas` que o front usa hoje **não existe**. Para a visão agregada da T10, o front itera os produtos de `GET /api/produtos` e chama `/{id}/metricas` de cada um (ou negociamos um endpoint agregado com o backend — divergência em aberto, ver §4).
- Sempre as 2 linhas da execução mais recente; lista **vazia** quando o motor nunca rodou.
- Acurácia exibida = `100 − mape`.

### 3.7 T5 — Alertas

`GET /api/alertas`

```json
// 200 — List<AlertaResponse> (vermelhos primeiro; dentro do grupo, menor diasAteRuptura)
[
  {
    "produtoId": 7,
    "nome": "Açúcar Cristal 1kg",
    "estoqueAtual": 10,
    "pontoReposicao": 31.20,
    "diasAteRuptura": 1.37,
    "leadTimeMedio": 3,
    "semaforo": "VERMELHO"
  }
]
```

- `semaforo` ∈ `"VERMELHO" | "AMARELO" | "VERDE"` — já calculado pelo backend, relativo ao PR (nunca recalcular no front com cortes de dias fixos).
- Produtos sem `pontoReposicao` (motor nunca rodou) **ficam fora da lista** — lista vazia ≠ "tudo verde"; combinar com o estado do motor.
- `leadTimeMedio` hoje é o default 3 (fornecedores reais são Pós-MVP).
- Quantidade sugerida de pedido: derivar de `pontoReposicao` − `estoqueAtual` + `estoqueSeguranca` (do detalhe) — **não** usar o `demanda × (leadTime + 7)` do protótipo.

### 3.8 T2 — Dashboard

`GET /api/dashboard`

```json
// 200 — DashboardResponse
{
  "riscoDeFaltar7Dias": 4,
  "criticoAgora": 2,
  "mapeMedioModeloSelecionado": 21.35,
  "seriesFaturamento": [
    { "semana": "2026-05-25", "total": 5412.80 },
    { "semana": "2026-06-01", "total": 6103.45 }
  ]
}
```

- `riscoDeFaltar7Dias` = produtos com `diasAteRuptura ≤ 7`; `criticoAgora` = `< 3`.
- `mapeMedioModeloSelecionado` usa o modelo **vencedor de cada produto** (não fixo no Prophet); `null` se o motor nunca rodou. Acurácia do card = `100 − mape`.
- `seriesFaturamento`: ~8 semanas de **histórico** (`semana` = segunda-feira). As 4 semanas **projetadas** do protótipo não vêm deste endpoint — se a tela for exibi-las, derivar das `previsoes` do detalhe ou deixar só o histórico no MVP.
- Card **"Valor em risco" não existe** no backend (o coeficiente ABRAS do protótipo foi descartado e a regra real está indefinida) — omitir o card por ora.

### 3.9 T7 — Curva ABC

`GET /api/curva-abc`

```json
// 200 — CurvaAbcResponse
{
  "abcProxy": false,
  "itens": [
    {
      "produtoId": 1,
      "nome": "Arroz 5kg",
      "classeAbc": "A",
      "faturamento": 122883.73,
      "percentualDoTotal": 35.42,
      "percentualAcumulado": 35.42
    }
  ]
}
```

- `itens` já vem ordenado por faturamento DESC com `percentualAcumulado` pronto — o gráfico de Pareto é plot direto.
- `abcProxy: true` → ranking por quantidade (histórico sem `valor_venda`); exibir a ressalva na tela.
- ⚠️ **Não há parâmetro `?periodo=`** — o filtro de período previsto no mapeamento ainda não existe no backend (divergência em aberto, §4). O ranking considera todo o histórico.

---

## 4. Divergências consolidadas

O que o wiki do front (`integracao-backend.md`) esperava × o que o backend realmente tem:

| Front esperava | Backend real | Ação sugerida |
|---|---|---|
| Rotas sem prefixo (`/auth/login`) | Tudo sob **`/api/...`** | Ajustar `API_BASE_URL`/rotas no `config.js` |
| `POST /importacao` único (multipart) | **2 endpoints**: `/api/importacao/produtos` + `/api/importacao/vendas` | Tela 3 faz 2 uploads (ordem: produtos → vendas) e depois chama o motor |
| Motor assíncrono / reload | `POST /api/motor/recalcular` **síncrono** (pode levar minutos) | Spinner bloqueante + timeout generoso; async (202 + status) fica p/ Épico 7 |
| `PATCH /produtos/{id}/parametros` | **Não existe** | Desabilitar o modal "Editar parâmetros" na T6; abrir task no backend |
| `GET /curva-abc?periodo=` | Existe **sem** `periodo` | Sem filtro de período no MVP; negociar parâmetro com o backend |
| `GET /produtos/metricas` (geral) | Só **`GET /api/produtos/{id}/metricas`** (por produto) | Front itera produtos, ou negociar endpoint agregado p/ T10 |
| `GET /sugestao-compra` | **Não existe** (Pós-MVP) | Tela 8 fica no mock |
| `PUT /configuracoes/*` | **Não existe** (Pós-MVP) | Tela 9 fica no mock (ou só logout) |
| `dias_ruptura` vem da API? | ✅ Sim: `diasAteRuptura` no detalhe e nos alertas (persistido pelo motor) | Consumir direto; não calcular no front |
| "Valor em risco": back ou front? | **Nenhum** — regra indefinida, card fora do MVP | Omitir o card |
| Campos derivados (PR, ES, tendência): back ou front? | ✅ Backend devolve tudo calculado | Consumir direto |

---

## 5. Checklist de integração (resumo executável)

1. Backend na `main` + MySQL (`docker-compose up -d db`) + ml-service `:8000` de pé.
2. **Pedir ao backend o CORS de dev** (bloqueador para chamadas do navegador).
3. `config.js`: `API_BASE_URL = http://localhost:8080/api`, desligar mock.
4. `requireAuth()` real: login → guardar JWT → header `Authorization` em todo fetch do `apiClient`.
5. Fluxo de fumaça (igual à coleção Postman): login → upload produtos → upload vendas → recalcular → conferir T4/T6/T10/T5/T2/T7.
6. Tratar os estados vazios: motor nunca rodou (campos `null`, alertas/métricas vazios) e `avisos[]` da importação.

> Dúvidas de shape: os DTOs Kotlin em `backend/src/main/kotlin/br/com/stocksense/dto/response/` são a fonte da verdade; a coleção Postman em `docs/postman/` permite ver cada response real com um clique.
