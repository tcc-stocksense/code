# Relatório Técnico — Motor Preditivo: Execução Assíncrona

> **StockSense · TCC 2026** — Decisão de arquitetura.
> Autor: gabrielb.duarte · Data: 2026-07-12 · Status: **✅ Validado com ressalvas pelo orientador (2026-07-12)**

> ⚠️ **Como ler.** Documenta a análise do desenho atual do motor, os riscos de carga
> identificados e o plano de evolução para execução assíncrona. Complementa
> `revisao-arquitetura.md`. As tarefas derivadas estão em `backend/tasks.md` (Épico 7) e
> `frontend/tasks.md` (seção "Motor assíncrono").

---

## Sumário executivo

**Em uma frase.** O motor preditivo hoje processa **todos os produtos numa única requisição
HTTP síncrona e sequencial**; com volume alto de SKUs isso leva minutos e estoura o timeout do
navegador/proxy. A decisão é tornar o lote **assíncrono** (resposta `202` imediata +
acompanhamento por status), mantendo um caminho síncrono apenas onde ele é barato (recálculo de
um único produto).

**Resultado da validação (2026-07-12).** Aprovado com ressalvas. Estado do job em memória e
contrato de status **aprovados** (contrato congelado); lote síncrono de debug **descartado**; três
lacunas viraram tarefas (guard de concorrência, warm-up do Prophet, benchmark). O **único item
ainda em aberto** é o **volume real de SKUs** (pendente do parceiro), que mantém o Épico 7
**SUSPENSO** — exceto o benchmark, que roda antes para calibrar a decisão. Detalhes na
seção [Decisões de validação](#7-decisões-de-validação-resolvidas-em-2026-07-12).

---

## 1. Contexto: o que o motor faz

O motor preditivo do StockSense está dividido em dois serviços:

- **ml-service** (Python/FastAPI, *stateless*): recebe o histórico de vendas de *um* produto,
  treina e compara Holt-Winters e Prophet, escolhe o modelo de menor MAPE e calcula os KPIs de
  estoque (ponto de reposição, estoque de segurança, dias até ruptura).
- **backend** (Kotlin/Spring Boot): orquestra — busca os produtos, chama o ml-service por
  produto (Feign) e persiste os resultados no MySQL.

### Pontos de entrada — projetado × implementado

| Gatilho | Documentado | Implementado hoje |
|---|---|---|
| `POST /api/motor/recalcular` | Sim | ✅ Sim — `MotorController` |
| Disparo após importação | Sim | ❌ Não — nenhum service de importação chama o motor |
| Cron mensal `@Scheduled` | Sim | ❌ Não — só nos docs, sem código |

**Conclusão:** hoje o único acionamento real é o endpoint manual. Os demais gatilhos existem
apenas no papel.

---

## 2. Diagnóstico: síncrono e sequencial

O fluxo é **100% síncrono e sequencial**, sem paralelismo, fila ou processamento em background
(confirmado por busca no código — não há `@Async`, `@Scheduled` nem `@EnableScheduling`). A
requisição HTTP só responde ao navegador depois que *todos* os produtos e a Curva ABC terminam.

```
HOJE — síncrono                         PROPOSTO — assíncrono
─────────────────────────               ─────────────────────────
POST /recalcular                        POST /recalcular
for cada produto (sequencial):          backend dispara em background
    Feign → POST /predict (bloqueia)    ← responde 202 na hora
    treina HW + Prophet (CPU)           front: GET /status a cada ~3s
recalcula ABC                           backend processa o lote
só então: responde  ← minutos           status = concluído → front recarrega
```

Holt-Winters é rápido, mas **Prophet é CPU-bound** (~1–5 s por produto, e a primeira chamada
compila o modelo Stan). Para ~312 SKUs em sequência, a estimativa é de **10 a 20+ minutos** numa
única requisição. O `read-timeout` Feign de 30 s protege *cada produto*, mas não o tempo agregado.

---

## 3. Riscos identificados

| Sev. | Risco | Descrição |
|---|---|---|
| 🔴 **Alta** | Timeout da requisição inteira | O `POST /recalcular` bloqueia por minutos; navegador, nginx ou load balancer cortam a conexão antes do fim. É o risco mais provável de aparecer numa demonstração. |
| 🟡 **Média** | ml-service single-worker | Uvicorn sobe com 1 worker e Prophet é CPU-bound — atende um `/predict` por vez, serializando o lote mesmo que o backend paralelizasse. |
| 🟡 **Média** | Cold start do Prophet | A primeira previsão após subir o container compila o modelo Stan e pode estourar os 30 s do Feign no primeiro produto. |
| 🟢 **Baixa** | Crescimento sem limpeza | Cada rodada faz *append* (~10 mil linhas por execução). Não é timeout, mas degrada consultas de "última rodada" ao longo do tempo. |
| 🟢 Baixa (carga) · 🔴 **Alta (validade acadêmica)** | `is_promocional` não enviado | O `montarRequest` não popula o regressor promocional do Prophet. Para **carga** o impacto é baixo; para a **validade da comparação Holt-Winters × Prophet é ALTO** — o regressor exógeno é uma **vantagem potencial do Prophet sendo desligada silenciosamente**, o que enviesa a comparação (núcleo acadêmico do TCC, Tela 10). Tratado na **T-55**: corrigir o `montarRequest` **ou** documentar explicitamente na metodologia que a comparação roda sem regressores exógenos. Não deixar a omissão silenciosa. |

### O que já está bem projetado

- **Transação por produto:** cada `executarMotor` roda na sua transação — uma falha isolada não
  aborta o lote inteiro.
- **Tratamento de falha do ml-service** → `MotorPreditivoException` → HTTP 502 com mensagem amigável.
- **Isolamento stateless** do ml-service e propriedade única do banco no backend.

---

## 4. Decisões de arquitetura

| # | Decisão | Racional |
|---|---|---|
| **D1** | **Núcleo único, duas cascas** | O loop do lote vira `processarLoteMotor()`; os endpoints síncrono/assíncrono e o scheduler são invólucros finos em volta dele. Adicionar/remover uma casca é reversível (~10 linhas) — a decisão não prende o projeto. |
| **D2** | **Editar estoque de 1 produto não re-roda o motor** | Previsão, ponto de reposição e estoque de segurança dependem do *histórico de vendas*, não do `estoque_atual`. Só mudam `dias_ate_ruptura` e o semáforo — aritmética barata, calculada na leitura das telas, sem chamar o ml-service. |
| **D3** | **O contrato do frontend é o que importa a longo prazo** | O contrato assíncrono (`202` + status) é um superconjunto: com poucos SKUs o status volta "concluído" quase instantâneo; com muitos, aguenta. O front fala com o async por padrão; o lote síncrono fica só como ferramenta de debug. |
| **D4** | **Quem faz o polling é o frontend** | O backend apenas expõe `GET /api/motor/status` (leitura idempotente). O loop que chama esse endpoint a cada ~3 s é responsabilidade do front — não existe "backend pollando". |
| **D5** | **Não há "endpoint de resultado" novo** | O resultado do motor é o banco atualizado. Ao concluir, o front apenas re-busca os endpoints de tela já existentes (`/dashboard`, `/produtos`, `/alertas`). |

---

## 5. Entregável — Épico 7 backend (`backend/tasks.md`)

| ID | Tarefa | Prioridade |
|---|---|---|
| `T-39` | Extrair núcleo compartilhado `processarLoteMotor()` | MVP |
| `T-40` | Estado do job em memória (`MotorJobStatus`) | MVP |
| `T-41` | `POST /api/motor/recalcular` assíncrono (202) | MVP |
| `T-42` | `GET /api/motor/status` | MVP |
| `T-43` | `POST /recalcular/{produtoId}` síncrono (1 produto) | MVP-opcional |
| `T-44` | Disparar motor ao fim da importação (**disparo único** no "Processar dados") | MVP |
| ~~`T-45`~~ | ~~Lote síncrono de debug~~ — **DESCARTADO na validação** | — |
| `T-46` | Testes: núcleo, async e status | MVP |
| `T-52` | **Guard de concorrência** (409 nos três gatilhos) | MVP |
| `T-53` | **Warm-up do Prophet** no startup do ml-service | MVP |
| `T-54` | **Benchmark do lote** (50/150/300 produtos) → tabela em `docs/` | **IMEDIATA** |
| `T-55` | `is_promocional` no `montarRequest` (corrigir **ou** documentar) | MVP |

> **T-54 (benchmark)** é a única tarefa que **roda antes** da confirmação do volume de SKUs — o
> resultado medido substitui a estimativa "10–20+ min" e será registrado em `docs/benchmark-motor.md`
> para a **metodologia do TCC**. As demais tarefas de async ficam **suspensas** até a confirmação.

---

## 6. Entregável — Frontend (`frontend/tasks.md`, seção "Motor assíncrono")

O "polling" e o "contrato final de dados" vivem inteiramente no front. O front usa o contrato
assíncrono por padrão.

| ID front | Tarefa | Backend relacionado | Prioridade |
|---|---|---|---|
| `F9` | Núcleo de acompanhamento do motor (`motorStatus.js`) — dispara, polla e reporta progresso/erro | T-41, T-42, T-47, T-48, T-51 | MVP |
| `S3+` | Ajustar Tela Importar ao fluxo assíncrono (consumir 202, progresso, recarregar ao concluir) | T-44, T-49 | MVP |
| `S6+` | Botão "recalcular este produto" (síncrono) na Tela Detalhe | T-43, T-50 | MVP-opcional |

Total do épico: **13 tarefas novas** (8 backend, 5 mapeadas em 3 tarefas de front). O scheduler
mensal (`T-35`) foi religado para reusar o núcleo `T-39`, evitando duplicar a lógica do lote.

---

## 7. Decisões de validação (resolvidas em 2026-07-12)

Os quatro pontos submetidos ao orientador foram decididos:

| # | Ponto | Decisão |
|---|---|---|
| 1 | **Volume real de SKUs** | ⏸️ **Pendente do parceiro.** Enquanto não confirmado, o **Épico 7 fica SUSPENSO** (não iniciar implementação). Se ~30, o lote roda em segundos e o épico vira *MVP-opcional*; se 300+, é *MVP*. A **T-54 (benchmark)** roda **antes** para substituir a estimativa por número medido e destravar a decisão. |
| 2 | **Estado do job em memória** | ✅ **Aprovado.** Limitação consciente documentada: *o estado se perde em restart; o lote é idempotente e pode ser re-disparado manualmente*. Sem tabela `execucao_motor` no escopo do TCC. |
| 3 | **Contrato de `GET /api/motor/status`** | ✅ **Aprovado e CONGELADO** como proposto. O frontend já pode depender do formato (`estado`, `feitos/total`, resumo ao concluir). |
| 4 | **Lote síncrono de debug** | ❌ **Descartado.** Não expor `/recalcular-sync`. O único caminho síncrono que permanece é o de **1 produto** (T-43). |

### Lacunas identificadas na revisão (viraram tarefas)

- **T-52 — Guard de concorrência.** `POST /api/motor/recalcular` retorna `409 Conflict` se já
  houver job `PROCESSANDO`. Vale para os **três gatilhos** (manual, pós-importação, cron), que
  passam pelo mesmo guard. O disparo pós-importação (T-44) ocorre **uma única vez**, no sucesso do
  "Processar dados" — nunca por planilha individual.
- **T-53 — Warm-up do Prophet.** Previsão *dummy* no `startup` do FastAPI, para a primeira chamada
  real não pagar a compilação Stan nem estourar o `read-timeout` de 30 s. Cobre o risco de cold start.
- **T-54 — Benchmark do lote.** Mede tempo total e por produto em 50/150/300 SKUs; resultado em
  `docs/benchmark-motor.md` para a metodologia. **Prioridade imediata.**
- **T-55 — `is_promocional`.** Risco reclassificado como **ALTO para a validade acadêmica** da
  comparação. Corrigir o `montarRequest` **ou** documentar na metodologia que a comparação roda sem
  regressores exógenos.

---

*Fonte: análise do código em `code/` e plano em `code/backend/tasks.md` (Épico 7). Gerado em 2026-07-12.*
