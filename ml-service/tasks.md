# Tasks — ml-service (Python / FastAPI)

> Organização por camada de responsabilidade: cada épico entrega uma peça coesa
> que pode ser executada e testada de forma independente.
>
> Legenda de prioridade: **MVP** · **MVP-opcional** · **Pós-MVP**
> Status: `[ ]` pendente · `[x]` concluído · `[-]` em progresso · `[~]` revisão necessária

---

## Estado atual

> Revisado em 2026-07-09 contra o código real (não apenas contra este arquivo, que
> estava desatualizado — descrevia o serviço como se nada tivesse sido implementado).

| Arquivo / Pasta | Situação |
|---|---|
| `Dockerfile` | ✅ Alinhado ao CLAUDE.md |
| `requirements.txt` | ✅ Completo (versões pinadas com `==`, não `>=` — funcionalmente equivalente) |
| `main.py` | ✅ Refatorado — registra `health_router` e `predict_router`, sem health check hardcoded |
| `app/__init__.py` e subpacotes | ✅ Estrutura de pastas criada |
| `app/models/` | ✅ `predict_request.py` e `predict_response.py` implementados |
| `app/services/` | ✅ `stock_service.py`, `holt_winters_service.py`, `prophet_service.py`, `prediction_service.py` implementados |
| `app/routers/` | ✅ `health_router.py`, `predict_router.py` implementados |
| `app/tests/` | ✅ `conftest.py` + testes de todos os services e do router (73/73 passam; ver nota sobre Prophet abaixo) |
| `.env.example` | ❌ Não existe — único item do Épico 0 realmente pendente (T-03) |

**Divergências corrigidas nesta revisão (2026-07-09):**
- `app/services/abc_service.py` e `app/tests/test_abc_service.py` existiam e ainda calculavam classe ABC dentro do `/predict` (campos `classe_abc`/`abc_proxy` no response), contrariando a ADR #3 (ABC vive no backend). O backend já contornava isso via `@JsonIgnoreProperties(ignoreUnknown = true)` e comentário citando "dívida técnica". **Removidos** — `prediction_service.py` não chama mais `classificar_abc`, e o response não tem mais esses campos.
- `desvio_padrao_demanda` (previsto desde a v1 deste `tasks.md`, T-06) não estava no `PredictResponse` — bloqueava a Tela 6. **Implementado**: `prediction_service.py` agora expõe o `σ` da série (já calculado internamente para Ballou) no campo `desvio_padrao_demanda`.
- **Pendência aberta para o backend** (fora do escopo deste arquivo): `PredictResponse.kt` ainda ignora `classe_abc`/`abc_proxy` (que não são mais enviados, então isso é inofensivo mas o comentário ficou desatualizado) e ainda não mapeia `desvio_padrao_demanda`. Atualizar `backend/CLAUDE.md` §4 e `PredictResponse.kt` fica para uma sessão focada no backend.

**Nota sobre testes (atualizada 2026-07-24):** `test_prophet_service.py` **passa 13/13** após o conserto do Prophet. A causa da falha antiga (`AttributeError: 'Prophet' object has no attribute 'stan_backend'`) **não** era CmdStan ausente — era conflito de versões: o `cmdstanpy 1.3.0` (sem pin) exige `makefile` no cmdstan empacotado do `prophet 1.1.6`, que não o tem. **Resolvido** pinando `cmdstanpy==1.2.4` no `requirements.txt`. Suíte completa do ml-service: **66 testes, 0 falhas**.

---

## Épico 0 — Fundação `MVP`

> Revisão e conclusão do setup. Pré-requisito para todos os épicos.

- [x] **T-01 — Revisar `Dockerfile`** `MVP`
  Confirmado alinhado ao CLAUDE.md §14:
  `FROM python:3.10-slim`, copia `requirements.txt`, instala, copia tudo, expõe 8000,
  roda `uvicorn main:app --host 0.0.0.0 --port 8000`.

- [x] **T-02 — Completar `requirements.txt`** `MVP`
  Todas as dependências do CLAUDE.md §2 presentes (`scikit-learn`, `scipy`, `pytest`,
  `pytest-asyncio`, `python-dotenv` incluídos). Versões pinadas com `==` em vez de
  `>=` — funcionalmente equivalente, mais reprodutível.

- [ ] **T-03 — Criar `.env.example`** `MVP`
  ```env
  APP_ENV=development
  LOG_LEVEL=INFO
  ML_SERVICE_PORT=8000
  ```
  Nunca commitar `.env` com valores reais. Apenas `.env.example` vai para o repositório.
  **Estado:** ainda não existe — único item do Épico 0 pendente.

- [x] **T-04 — Refatorar `main.py`** `MVP`
  `main.py` instancia `FastAPI` com `title`/`version` e registra `health_router` e
  `predict_router` via `app.include_router()`. Sem health check hardcoded.
  **Pendência residual:** não carrega `.env` com `python-dotenv` (depende de T-03 existir
  para fazer sentido carregar algo).

---

## Épico 1 — Schemas Pydantic `MVP`

> Contrato de entrada e saída entre backend e ml-service.
> Definir antes de qualquer service — é a interface que tudo implementa.

- [x] **T-05 — `app/models/predict_request.py`** `MVP`
  Implementado exatamente conforme o contrato (usa `default_factory=list` para
  `is_promocional` em vez de `default=[]` — equivalente e mais correto no Pydantic v2).
  _Depende de: T-01_

- [x] **T-06 — `app/models/predict_response.py`** `MVP`
  Implementado. `desvio_padrao_demanda` foi adicionado nesta revisão (2026-07-09) —
  faltava e bloqueava a Tela 6. `classe_abc`/`abc_proxy` foram removidos nesta mesma
  revisão (existiam por engano — ABC migrou para o backend, ADR #3).
  ⚠️ **Sem `classe_abc`** — ABC migrou para o backend (`AbcService`).
  ⚠️ `float("inf")` é inválido em JSON — `dias_ate_ruptura` é `float | None`.
  _Depende de: T-01_

---

## Épico 2 — Stock Service `MVP`

> Cálculos de KPIs de estoque: pura matemática, sem dependência de ML.
> Implementar e testar antes dos modelos preditivos — serve de validação das fórmulas.

- [x] **T-07 — `app/services/stock_service.py`** `MVP`
  Implementar as quatro funções com docstrings obrigatórias:

  `calcular_z_score(nivel_servico: float) -> float`
  Usa `scipy.stats.norm.ppf`. Ex: 0.95 → 1.645.

  `calcular_estoque_seguranca(z, lead_time_medio, desvio_demanda, demanda_media, variabilidade_lead_time) -> float`
  Fórmula de Ballou (2006): `Z * sqrt(LT * σ²_demanda + demanda² * σ²_lead_time)`.

  `calcular_ponto_reposicao(demanda_media, lead_time_medio, estoque_seguranca) -> float`
  `demanda_media * lead_time_medio + estoque_seguranca`.

  `calcular_dias_ate_ruptura(estoque_atual: int, demanda_media_diaria: float) -> float | None`
  Retorna `None` quando `demanda_media_diaria <= 0` — nunca dividir por zero,
  nunca retornar `float("inf")`.
  _Depende de: T-01_
  **Estado:** implementado — as quatro funções existem com docstrings completas.

- [x] **T-08 — Testes: `app/tests/test_stock_service.py`** `MVP`
  Cenários obrigatórios:
  - Z-score: `nivel_servico=0.95` → `z ≈ 1.645`; `nivel_servico=0.99` → `z ≈ 2.326`
  - Estoque de segurança: valores conhecidos contra a fórmula de Ballou
  - Ponto de reposição: `demanda=10, lead_time=3, ES=5` → `PR=35`
  - Dias até ruptura: `estoque=40, demanda=5.0` → `8.0`
  - Dias até ruptura com `demanda=0` → `None` (não `inf`, não exception)
  _Depende de: T-07_
  **Estado:** todos os cenários cobertos, suíte passa.

---

## Épico 3 — Model Services `MVP`

> Implementações isoladas dos dois modelos de séries temporais.
> Cada service expõe apenas `treinar_e_avaliar()`.
> Holt-Winters e Prophet podem ser implementados em paralelo — sem dependência mútua.

- [x] **T-09 — `app/services/holt_winters_service.py`** `MVP`
  Implementado com todos os pontos do contrato: `ExponentialSmoothing` com fallback
  de sazonalidade para séries curtas, walk-forward 80/20, previsão de 30 dias.
  **Divergência menor (não bloqueante):** o limiar de fallback usa `len(serie) >= 2 * seasonal_periods`
  (14 dias) e mínimo de 10 observações não-nulas — mais rigoroso que o texto original ("< 14 dias"),
  mesmo comportamento na prática.
  _Depende de: T-05, T-06_

- [ ] **T-10 — `app/services/prophet_service.py`** `MVP` / `MVP-opcional`
  Implementado (walk-forward, fallback de sazonalidade, previsão de 30 dias).
  **Pendência real:** a assinatura pública ficou `treinar_e_avaliar(serie)` — **sem** o
  parâmetro `is_promocional`. O regressor promocional (`MVP-opcional`) não foi implementado;
  `model.add_regressor("is_promocional")` do CLAUDE.md §6 não existe no código.
  _Depende de: T-05, T-06_

- [x] **T-11 — Testes: `app/tests/test_holt_winters_service.py`** `MVP`
  Todos os cenários cobertos, suíte passa.
  _Depende de: T-09_

- [x] **T-12 — Testes: `app/tests/test_prophet_service.py`** `MVP`
  **13/13 passam (resolvido 2026-07-24).** A falha antiga (`AttributeError: 'Prophet' object
  has no attribute 'stan_backend'`) **não** era CmdStan ausente nem bug de código — era conflito
  de versões: `cmdstanpy 1.3.0` (puxado sem pin) exige `makefile` no cmdstan empacotado do
  `prophet 1.1.6`, que vem sem ele; o `prophet_model.bin` já é pré-compilado. **Conserto:** pin
  `cmdstanpy==1.2.4` no `requirements.txt` (NÃO reinstalar prophet — mesmo par de versões traz o
  mesmo erro; NÃO precisa de Rtools/`install_cmdstan`).
  _Depende de: T-10_

---

## Épico 4 — Prediction Service (Orquestração) `MVP`

> Orquestra os dois modelos, seleciona o vencedor e monta o `PredictResponse` completo.
> Depende de todos os services anteriores.

- [x] **T-13 — `app/services/prediction_service.py`** `MVP`
  Função principal: `async def executar_previsao(request: PredictRequest) -> PredictResponse`

  Fluxo obrigatório (na ordem):
  1. Converter `historico` em `pd.Series` com índice de datas
  2. Validar: se `len(historico) < 90` → lançar `ValueError("Mínimo de 90 dias de histórico necessário")`
  3. Logar: `[produto_id=X] Iniciando previsão`
  4. Chamar `holt_winters_service.treinar_e_avaliar()` — capturar exception se falhar
  5. Chamar `prophet_service.treinar_e_avaliar()` — capturar exception se falhar
  6. Se **ambos falharem** → lançar `Exception` com mensagem descritiva
  7. Selecionar modelo vencedor pelo **menor MAPE** (ou o único disponível se um falhou)
  8. Logar MAPEs de cada modelo e qual foi selecionado
  9. Chamar `stock_service` para calcular ES, PR, dias até ruptura e σ (desvio padrão da série)
  10. Montar e retornar `PredictResponse`

  Tratamento de erros e casos especiais (§9 do CLAUDE.md):
  | Caso | Comportamento |
  |---|---|
  | Série com zeros excessivos (> 30%) | Log de aviso + continuar |
  | Prophet falha | Usar só Holt-Winters, logar motivo |
  | Holt-Winters falha | Usar só Prophet, logar motivo |
  | MAPE > 50% no vencedor | Preencher `aviso` no response |
  | `demanda_media = 0` | `dias_ate_ruptura = None` |

  _Depende de: T-06, T-07, T-09, T-10_
  **Estado:** implementado, incluindo captura isolada de falha por modelo e o campo
  `desvio_padrao_demanda` adicionado nesta revisão. A chamada a `classificar_abc` (ABC)
  que existia aqui foi removida — não fazia parte deste contrato (ver "Estado atual").

---

## Épico 5 — Routers + `main.py` final `MVP`

> Camada HTTP. Implementar após os schemas e services estarem prontos.

- [x] **T-14 — `app/routers/health_router.py`** `MVP`
  Implementado (retorna também `service` e `version`, além de `status`).
  _Depende de: T-01_

- [x] **T-15 — `app/routers/predict_router.py`** `MVP`
  Implementado — trata `ValueError` (422) e `RuntimeError`/`Exception` genérica (500)
  separadamente, com log antes de responder. Stack trace não vaza ao cliente.
  _Depende de: T-05, T-06, T-13_

- [x] **T-16 — Finalizar `main.py`** `MVP`
  `health_router` e `predict_router` registrados via `app.include_router()`.
  Sem `@app.get("/health")` hardcoded.
  _Depende de: T-04, T-14, T-15_

---

## Épico 6 — Testes de Integração `MVP`

- [x] **T-17 — `app/tests/conftest.py`** `MVP`
  Fixtures implementadas e mais completas que o pedido original: `serie_90_dias`
  (com sazonalidade semanal sintética e seed fixa), `serie_curta`,
  `serie_com_zeros_excessivos`, `payload_valido`.
  _Depende de: T-01_

- [x] **T-18 — `app/tests/test_predict_router.py`** `MVP`
  Implementado com `TestClient` síncrono + mock de `executar_previsao` (em vez de
  `httpx.AsyncClient` chamando os services de verdade) — mantém os testes rápidos e
  focados no roteamento HTTP. Cobre validação (422), sucesso (200 com todos os campos
  do schema), erro interno (500 sem vazar stack trace) e `GET /health`.
  _Depende de: T-15, T-16, T-17_

---

## Pós-MVP

- [ ] **T-19 — Versionamento de modelo / monitoramento de drift** `Pós-MVP`
  Registrar qual versão do modelo foi usada em cada execução.
  Detectar degradação de MAPE ao longo do tempo.

---

## Sumário

| Épico | Entrega | Tasks | Prioridade | Status |
|---|---|---|---|---|
| 0 — Fundação | Dockerfile ✅, requirements ✅, `.env.example` ❌, `main.py` ✅ | T-01 → T-04 | MVP | 3/4 |
| 1 — Schemas | `PredictRequest` e `PredictResponse` (contrato com backend) | T-05 → T-06 | MVP | 2/2 |
| 2 — Stock Service | Fórmulas de ES, PR, ruptura (Ballou) + testes | T-07 → T-08 | MVP | 2/2 |
| 3 — Model Services | Holt-Winters ✅ + Prophet ✅ (sem `is_promocional`) + testes ✅ (Prophet consertado 2026-07-24) | T-09 → T-12 | MVP | 3/4 |
| 4 — Prediction Service | Orquestração, seleção de modelo, tratamento de erros | T-13 | MVP | 1/1 |
| 5 — Routers | `GET /health`, `POST /predict`, `main.py` final | T-14 → T-16 | MVP | 3/3 |
| 6 — Testes integração | Fixtures + testes do router | T-17 → T-18 | MVP | 2/2 |
| Pós-MVP | Versionamento / drift | T-19 | Pós-MVP | 0/1 |

**16/19 tasks concluídas.** Pendências reais: T-03 (`.env.example`), T-10 (regressor
`is_promocional` no Prophet, opcional), T-19 (Pós-MVP, não é prioridade agora).
T-12 (Prophet) **resolvida em 2026-07-24** — pin `cmdstanpy==1.2.4`.

---

## Como rodar os testes

```bash
# Na raiz do ml-service (com venv ativado):
pytest app/tests/ -v --tb=short
```

---

*Atualizar o status (`[ ]` → `[x]`) conforme as tasks forem concluídas.*
