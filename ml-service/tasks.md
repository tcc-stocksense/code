# Tasks — ml-service (Python / FastAPI)

> Organização por camada de responsabilidade: cada épico entrega uma peça coesa
> que pode ser executada e testada de forma independente.
>
> Legenda de prioridade: **MVP** · **MVP-opcional** · **Pós-MVP**
> Status: `[ ]` pendente · `[x]` concluído · `[-]` em progresso · `[~]` revisão necessária

---

## Estado atual

| Arquivo / Pasta | Situação |
|---|---|
| `Dockerfile` | ✅ Alinhado ao CLAUDE.md |
| `requirements.txt` | ⚠️ Incompleto — faltam `scikit-learn`, `scipy`, `pytest`, `pytest-asyncio`, `python-dotenv` |
| `main.py` | ⚠️ Health check hardcoded (sem router), sem dotenv, sem registro de routers |
| `app/__init__.py` e subpacotes | ✅ Estrutura de pastas criada |
| `app/routers/`, `services/`, `models/`, `tests/` | ❌ Apenas `__init__.py` — zero implementação |

---

## Épico 0 — Fundação `MVP`

> Revisão e conclusão do setup. Pré-requisito para todos os épicos.

- [~] **T-01 — Revisar `Dockerfile`** `MVP`
  Confirmar que está alinhado ao CLAUDE.md §14:
  `FROM python:3.10-slim`, copia `requirements.txt`, instala, copia tudo, expõe 8000,
  roda `uvicorn main:app --host 0.0.0.0 --port 8000`.
  **Estado:** arquivo existe e está correto — marcar como concluído após leitura.

- [~] **T-02 — Completar `requirements.txt`** `MVP`
  Adicionar dependências faltantes:
  ```
  scikit-learn>=1.4.0
  scipy>=1.11.0
  pytest>=8.0.0
  pytest-asyncio>=0.23.0
  python-dotenv>=1.0.0
  ```
  Versões já presentes no arquivo devem ser conferidas contra o CLAUDE.md §2.
  **Estado:** arquivo existe mas está incompleto — requer edição.

- [ ] **T-03 — Criar `.env.example`** `MVP`
  ```env
  APP_ENV=development
  LOG_LEVEL=INFO
  ML_SERVICE_PORT=8000
  ```
  Nunca commitar `.env` com valores reais. Apenas `.env.example` vai para o repositório.

- [~] **T-04 — Refatorar `main.py`** `MVP`
  O `main.py` atual tem health check hardcoded e não carrega `.env`.
  Refatorar para:
  1. Carregar variáveis de ambiente com `python-dotenv` (`load_dotenv()`)
  2. Instanciar o `FastAPI` com `title` e `version`
  3. Registrar routers via `app.include_router()` (health e predict)
  4. Remover o `@app.get("/health")` hardcoded
  **Atenção:** só registrar os routers após T-11 e T-12 (Épico 3) estarem prontos.
  Implementar o carregamento de dotenv agora; deixar `include_router` para T-13.
  **Estado:** arquivo existe mas precisa de refatoração.

---

## Épico 1 — Schemas Pydantic `MVP`

> Contrato de entrada e saída entre backend e ml-service.
> Definir antes de qualquer service — é a interface que tudo implementa.

- [ ] **T-05 — `app/models/predict_request.py`** `MVP`
  ```python
  class VendaDiaria(BaseModel):
      data: date
      quantidade: int = Field(gt=0)

  class PredictRequest(BaseModel):
      produto_id: int
      historico: list[VendaDiaria] = Field(min_length=90)
      lead_time_medio: int = Field(default=3, ge=1)
      variabilidade_lead_time: float = Field(default=1.0, ge=0)
      nivel_servico_alvo: float = Field(default=0.95, ge=0.5, le=0.999)
      estoque_atual: int = Field(ge=0)
      is_promocional: list[int] = Field(default=[])
  ```
  _Depende de: T-01_

- [ ] **T-06 — `app/models/predict_response.py`** `MVP`
  ```python
  class MetricasModelo(BaseModel):
      mape: float
      rmse: float
      mae: float

  class PrevisaoDiaria(BaseModel):
      data: date
      quantidade_prevista: float

  class PredictResponse(BaseModel):
      produto_id: int
      modelo_selecionado: str               # "holt_winters" | "prophet"
      previsoes: list[PrevisaoDiaria]       # 30 pontos diários
      metricas: dict[str, MetricasModelo]   # alimenta Tela 10
      ponto_reposicao: float
      estoque_seguranca: float
      dias_ate_ruptura: float | None        # None quando demanda média = 0
      desvio_padrao_demanda: float          # acordo cross-service (T-05 do backend)
      aviso: str | None = None             # MAPE > 50% — MVP-opcional
  ```
  ⚠️ **Sem `classe_abc`** — ABC migrou para o backend (`AbcService`).
  ⚠️ `float("inf")` é inválido em JSON — `dias_ate_ruptura` é `float | None`.
  _Depende de: T-01_

---

## Épico 2 — Stock Service `MVP`

> Cálculos de KPIs de estoque: pura matemática, sem dependência de ML.
> Implementar e testar antes dos modelos preditivos — serve de validação das fórmulas.

- [ ] **T-07 — `app/services/stock_service.py`** `MVP`
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

- [ ] **T-08 — Testes: `app/tests/test_stock_service.py`** `MVP`
  Cenários obrigatórios:
  - Z-score: `nivel_servico=0.95` → `z ≈ 1.645`; `nivel_servico=0.99` → `z ≈ 2.326`
  - Estoque de segurança: valores conhecidos contra a fórmula de Ballou
  - Ponto de reposição: `demanda=10, lead_time=3, ES=5` → `PR=35`
  - Dias até ruptura: `estoque=40, demanda=5.0` → `8.0`
  - Dias até ruptura com `demanda=0` → `None` (não `inf`, não exception)
  _Depende de: T-07_

---

## Épico 3 — Model Services `MVP`

> Implementações isoladas dos dois modelos de séries temporais.
> Cada service expõe apenas `treinar_e_avaliar()`.
> Holt-Winters e Prophet podem ser implementados em paralelo — sem dependência mútua.

- [ ] **T-09 — `app/services/holt_winters_service.py`** `MVP`
  Única função pública:
  ```python
  def treinar_e_avaliar(serie: pd.Series) -> tuple[MetricasModelo, pd.Series]:
  ```
  Implementação:
  - `ExponentialSmoothing(trend="add", seasonal="add", seasonal_periods=7, initialization_method="estimated")`
  - Validação walk-forward: treinar nos primeiros 80%, avaliar nos últimos 20%
  - Métricas: MAPE, RMSE (sklearn), MAE (sklearn)
  - **Nunca `train_test_split`** — embaralha a série temporal
  - Fallback: se série < 14 dias, usar `seasonal=None` e logar aviso
  - Previsão: próximos 30 dias com o modelo treinado em toda a série
  _Depende de: T-05, T-06_

- [ ] **T-10 — `app/services/prophet_service.py`** `MVP` / `MVP-opcional`
  Única função pública:
  ```python
  def treinar_e_avaliar(serie: pd.Series, is_promocional: list[int] = []) -> tuple[MetricasModelo, pd.Series]:
  ```
  Implementação:
  - `Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False, interval_width=0.95)`
  - Renomear colunas para `ds` e `y` **dentro deste service** — nunca no `prediction_service`
  - Regressor `is_promocional` se lista não vazia — `MVP-opcional`
  - Walk-forward: treinar em 80%, avaliar em 20%
  - Métricas: MAPE, RMSE, MAE
  - Previsão: próximos 30 dias
  _Depende de: T-05, T-06_

- [ ] **T-11 — Testes: `app/tests/test_holt_winters_service.py`** `MVP`
  Cenários obrigatórios:
  - Série normal com 90 dias → retorna `MetricasModelo` e série de 30 previsões
  - Série com > 30% de zeros → continua (com log de aviso)
  - Série com < 14 dias → fallback `seasonal=None`, sem exception
  _Depende de: T-09_

- [ ] **T-12 — Testes: `app/tests/test_prophet_service.py`** `MVP`
  Cenários obrigatórios:
  - Série normal com 90 dias → retorna `MetricasModelo` e série de 30 previsões
  - Série sem coluna `is_promocional` (lista vazia) → funciona normalmente
  _Depende de: T-10_

---

## Épico 4 — Prediction Service (Orquestração) `MVP`

> Orquestra os dois modelos, seleciona o vencedor e monta o `PredictResponse` completo.
> Depende de todos os services anteriores.

- [ ] **T-13 — `app/services/prediction_service.py`** `MVP`
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

---

## Épico 5 — Routers + `main.py` final `MVP`

> Camada HTTP. Implementar após os schemas e services estarem prontos.

- [ ] **T-14 — `app/routers/health_router.py`** `MVP`
  ```python
  router = APIRouter(tags=["health"])

  @router.get("/health")
  def health():
      return {"status": "ok"}
  ```
  _Depende de: T-01_

- [ ] **T-15 — `app/routers/predict_router.py`** `MVP`
  ```python
  router = APIRouter(prefix="/predict", tags=["predict"])

  @router.post("", response_model=PredictResponse)
  async def predict(request: PredictRequest) -> PredictResponse:
      try:
          return await executar_previsao(request)
      except ValueError as e:
          raise HTTPException(status_code=422, detail=str(e))
      except Exception:
          # stack trace vai apenas para o log — nunca para o cliente
          raise HTTPException(status_code=500, detail="Erro interno no motor preditivo")
  ```
  _Depende de: T-05, T-06, T-13_

- [~] **T-16 — Finalizar `main.py`** `MVP`
  Concluir a refatoração iniciada em T-04:
  registrar `health_router` e `predict_router` via `app.include_router()`.
  Remover definitivamente o `@app.get("/health")` hardcoded.
  _Depende de: T-04, T-14, T-15_

---

## Épico 6 — Testes de Integração `MVP`

- [ ] **T-17 — `app/tests/conftest.py`** `MVP`
  Fixtures reutilizáveis:
  ```python
  @pytest.fixture
  def serie_90_dias() -> pd.Series:
      """Série temporal sintética com 90 dias."""
      datas = pd.date_range(start="2025-01-01", periods=90, freq="D")
      quantidades = np.random.randint(5, 30, size=90)
      return pd.Series(quantidades, index=datas)

  @pytest.fixture
  def payload_valido() -> dict:
      """Payload mínimo válido para POST /predict."""
      return {
          "produto_id": 1,
          "historico": [
              {"data": f"2025-{(i//30)+1:02d}-{(i%30)+1:02d}", "quantidade": 10 + i % 5}
              for i in range(90)
          ],
          "lead_time_medio": 3,
          "variabilidade_lead_time": 1.0,
          "nivel_servico_alvo": 0.95,
          "estoque_atual": 40,
      }
  ```
  _Depende de: T-01_

- [ ] **T-18 — `app/tests/test_predict_router.py`** `MVP`
  Usar `httpx.AsyncClient` com `app` do FastAPI.
  Cenários obrigatórios:
  - `POST /predict` com `payload_valido` → 200, response com todos os campos do schema
  - `POST /predict` com `historico` de < 90 dias → 422 com mensagem clara
  - `POST /predict` com `quantidade <= 0` em algum registro → 422 (validação Pydantic)
  - `GET /health` → 200 `{"status": "ok"}`
  _Depende de: T-15, T-16, T-17_

---

## Pós-MVP

- [ ] **T-19 — Versionamento de modelo / monitoramento de drift** `Pós-MVP`
  Registrar qual versão do modelo foi usada em cada execução.
  Detectar degradação de MAPE ao longo do tempo.

---

## Sumário

| Épico | Entrega | Tasks | Prioridade |
|---|---|---|---|
| 0 — Fundação | Dockerfile ✅, requirements completo, `.env.example`, `main.py` preparado | T-01 → T-04 | MVP |
| 1 — Schemas | `PredictRequest` e `PredictResponse` (contrato com backend) | T-05 → T-06 | MVP |
| 2 — Stock Service | Fórmulas de ES, PR, ruptura (Ballou) + testes | T-07 → T-08 | MVP |
| 3 — Model Services | Holt-Winters + Prophet isolados + testes | T-09 → T-12 | MVP |
| 4 — Prediction Service | Orquestração, seleção de modelo, tratamento de erros | T-13 | MVP |
| 5 — Routers | `GET /health`, `POST /predict`, `main.py` final | T-14 → T-16 | MVP |
| 6 — Testes integração | Fixtures + testes do router | T-17 → T-18 | MVP |
| Pós-MVP | Versionamento / drift | T-19 | Pós-MVP |

**19 tasks no total.** Épicos em ordem estrita de dependência — não pular.

---

## Como rodar os testes

```bash
# Na raiz do ml-service (com venv ativado):
pytest app/tests/ -v --tb=short
```

---

*Atualizar o status (`[ ]` → `[x]`) conforme as tasks forem concluídas.*
