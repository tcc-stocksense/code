# Revisão de Arquitetura — StockSense

> **Objetivo:** validar, de forma metódica, se a implementação atual está fiel às decisões
> de arquitetura registradas — e se essas decisões ainda fazem sentido para o objetivo do
> TCC (demonstrar empiricamente o motor preditivo **Holt-Winters × Prophet**).
>
> **Como usar:** percorra cada item, confira contra o código, e preencha o **Status**.
> Reserve 1–2h. Onde já há um achado pré-preenchido, o trabalho é só **confirmar**.

**Legenda de status:** ✅ implementado e fiel · ⚠️ diverge / decisão pendente · ❌ viola a decisão · ⬜ ainda não revisado

**Método — 3 perguntas por decisão:**
1. A decisão **ainda faz sentido** para o objetivo do TCC?
2. O código **realmente a implementa**, ou divergiu?
3. Se divergiu, foi **consciente** (decisão nova, ok registrar) ou **acidental** (dívida técnica)?

---

## Parte A — Regras de fluxo (invariantes)

Fonte: `CLAUDE.md` raiz §3 e §10. São as fronteiras que **não podem** ser violadas.

| # | Invariante | Como verificar | Status | Achado atual |
|---|---|---|---|---|
| A1 | Frontend **nunca** chama o ml-service direto — só a API | Buscar no `frontend/` chamadas HTTP; conferir que apontam só para o backend | ⬜ | Frontend ainda é mock (sem chamadas HTTP reais); **garantir isso quando integrar** |
| A2 | ml-service é **stateless** — não acessa banco | `ml-service/requirements.txt` não tem driver de BD; nenhum `import` de SQLAlchemy/psycopg/mysql | ✅ | Confirmar: sem dependência de BD no ml-service |
| A3 | Backend é o **único dono do banco** | Só o backend tem JDBC/JPA; ml-service não persiste | ✅ | Confirmar |
| A4 | API é **orquestradora** (valida, aciona motor, persiste, expõe) | `MotorController`/`MotorService` acionam o ML e persistem | ✅ | Confirmar |
| A5 | Contrato `/predict` mudou de um lado → atualiza o outro | Comparar Pydantic (ml-service) × DTO Feign (backend) — ver Parte C | ⚠️ | Ver divergências na Parte C |

---

## Parte B — Os 7 ADRs (decisões de arquitetura)

Fonte: `CLAUDE.md` raiz §9. Uma seção por decisão.

### ADR #1 — MySQL 8.0 como SGBD único
- **Decisão:** MySQL único; sem PostgreSQL no projeto.
- **Como verificar:** `docker-compose.yml` usa `mysql:8.0`; `application.yml` usa `MySQLDialect`; nenhuma dependência/menção a Postgres no código (só em docs antigas marcadas como desatualizadas).
- **Status:** ✅ (confirmar) — **Notas:** ______________________

### ADR #2 — ml-service stateless (não persiste)
- **Decisão:** o motor recebe JSON, devolve JSON, não toca no banco.
- **Como verificar:** `ml-service/requirements.txt` sem driver de BD; nenhum acesso a banco nos services Python.
- **Status:** ✅ (confirmar) — **Notas:** ______________________

### ADR #3 — Classificação ABC no backend
- **Decisão:** ABC é ranking relativo entre todos os produtos → vive no backend (`AbcService`), não no ml-service.
- **Como verificar:** backend tem `AbcService` ✅. `abc_service.py`/`test_abc_service.py` foram removidos do ml-service em 2026-07-09; `prediction_service.py` não calcula mais `classe_abc`/`abc_proxy`.
- **Status:** ✅ **resolvido em 2026-07-09** — *boundary leak* eliminado; nenhum dos dois lados calcula ABC fora do backend agora. **Notas:** ______________________

### ADR #4 — Login no estabelecimento (sem tabela `usuario`)
- **Decisão:** uma credencial por mercado; login não é o foco.
- **Como verificar:** entidade `Estabelecimento` com `email`/`senhaHash`; sem tabela `usuario`. (Código na branch `feat/auth-login-jwt`.)
- **Status:** ✅ (confirmar) — **Notas:** ______________________

### ADR #5 — Preparado para multi-estabelecimento
- **Decisão:** `estabelecimento_id` em `produto`, embora só 1 mercado seja cadastrado.
- **Como verificar:** coluna `estabelecimento_id` no `V1`; campo `estabelecimentoId` na entidade `Produto`; queries do ABC/Motor filtram por estabelecimento.
- **Status:** ✅ (confirmar) — **Ponto de atenção:** só há 1 estabelecimento seedado; o filtro existe mas nunca foi exercitado com 2+. **Notas:** ______________________

### ADR #6 — ESG fora do escopo
- **Decisão:** sem `perda_estoque`, sem KPI de desperdício, sem planilha de perdas.
- **Como verificar:** `grep perda_estoque` no código → só aparece em docs como "removido"; sem tabela no `V1`.
- **Status:** ✅ (confirmar) — **Notas:** ______________________

### ADR #7 — `previsao` / `metrica_modelo` separadas
- **Decisão:** pontos diários e métricas por modelo têm cardinalidades diferentes; suporta a Tela 10.
- **Como verificar:** duas tabelas no `V1`; entidades `Previsao` e `MetricaModelo`; `MotorService` grava 30 previsões + 2 métricas por execução.
- **Status:** ✅ (confirmar) — **Notas:** ______________________

---

## Parte C — Contrato `/predict` (a fronteira backend ↔ ML)

Comparar o Pydantic do ml-service (`app/models/predict_response.py`) com o DTO Feign do
backend (`client/dto/PredictResponse.kt`). É onde divergência dói mais.

| Campo (ml-service, snake_case) | No response do ml-service? | No DTO Feign do backend? | Observação |
|---|---|---|---|
| `produto_id` | ✅ | ✅ | — |
| `modelo_selecionado` | ✅ | ✅ | — |
| `previsoes` | ✅ | ✅ | 30 pontos |
| `metricas` | ✅ | ✅ | alimenta a Tela 10 |
| `ponto_reposicao` | ✅ | ✅ | — |
| `estoque_seguranca` | ✅ | ✅ | — |
| `dias_ate_ruptura` | ✅ | ✅ | nullable |
| `aviso` | ✅ | ✅ | MAPE > 50% |
| `classe_abc` | ✅ removido em 2026-07-09 | nunca existiu no DTO | *boundary leak* corrigido — `abc_service.py` deletado do ml-service |
| `abc_proxy` | ✅ removido em 2026-07-09 | nunca existiu no DTO | idem |
| `desvio_padrao_demanda` | ✅ devolvido desde 2026-07-09 | ✅ mapeado em 2026-07-10 | **T-05 resolvido** — `MotorService` grava em `produto.desvioPadraoDemanda`, testado (`MotorServiceTest`) |

**Decisão tomada (T-05):** ✅ o ml-service passa a devolver `desvio_padrao_demanda` (opção *a*, como recomendado) — resolvido em 2026-07-10.

---

## Parte D — Perguntas de stress-test (para a banca)

Perguntas que uma banca provavelmente faria. Ter a resposta pronta fortalece a defesa.

| Pergunta | Resposta preliminar | Precisa decidir? |
|---|---|---|
| O **ml-service stateless** se justifica ou é complexidade a mais? | Justifica: isola o motor, permite trocar/comparar modelos sem tocar no backend. Bom argumento de engenharia. | Não — só documentar bem |
| A **comunicação síncrona (Feign, 30s por produto)** aguenta ~312 SKUs × 2 modelos? | Recalcular tudo pode levar **minutos**. No MVP roda via cron mensal, então é tolerável. | ⚠️ **Sim** — decidir se aceita no MVP ou evolui p/ batch/assíncrono; registrar como limitação conhecida |
| **Login por estabelecimento** (sem multi-usuário) basta? | Sim — login não é o foco do TCC; evolução futura é aditiva. | Não |
| A separação **`previsao`/`metrica_modelo`** sustenta a Tela 10? | Sim — é a fonte do comparativo HW × Prophet, núcleo acadêmico. | Não |
| O **lead time no default (3/1.0)** compromete o ponto de reposição? | O ponto de reposição é um KPI central; sem `ProdutoFornecedor` ele usa sempre o default. | ⚠️ **Sim** — decidir se implementa `Fornecedor`/`ProdutoFornecedor` (MVP-opcional) para ter lead time real |

---

## Parte E — Síntese e próximos passos

Preencher ao final da revisão.

- **Decisões que continuam válidas:** ______________________
- **Decisões a revisar/mudar:** ______________________
- **Dívidas técnicas confirmadas:**
  - [x] Remover ABC (`classe_abc`/`abc_proxy`) do ml-service (ADR #3) — resolvido 2026-07-09
  - [x] Resolver T-05 (`desvio_padrao_demanda`) — resolvido 2026-07-10
  - [ ] Decidir sobre lead time real (`Fornecedor`/`ProdutoFornecedor`)
  - [ ] Definir postura sobre performance do recálculo síncrono
  - [ ] ______________________
- **Itens para registrar no TCC (demonstram maturidade de engenharia):** ______________________

---

*Documento de apoio à revisão. Atualizar o status conforme a revisão for feita.*
