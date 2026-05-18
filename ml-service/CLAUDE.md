# CLAUDE.md — ml-service (Motor Preditivo / StockSense)
> Instruções específicas do serviço Python. Leia este arquivo e o CLAUDE.md da raiz antes de qualquer ação.

---

## 1. Responsabilidade do Serviço

O ml-service é o **cérebro preditivo** do StockSense. Ele não gerencia usuários, não faz autenticação, não conhece o frontend. Sua única responsabilidade é:

1. Receber um histórico de vendas por produto
2. Treinar e comparar dois modelos de séries temporais (Holt-Winters e Prophet)
3. Selecionar o modelo de melhor desempenho por produto
4. Calcular KPIs de estoque: estoque de segurança, ponto de reposição, dias até ruptura, classificação ABC
5. Retornar tudo via JSON para o backend (Spring Boot)

**Este serviço é síncrono.** O backend chama, o Python processa e responde na mesma requisição.
Timeout máximo esperado pelo backend (Feign Client): **30 segundos**.

---

## 2. Stack Tecnológica

| Biblioteca | Versão mínima | Finalidade |
|---|---|---|
| Python | 3.10+ | Linguagem principal |
| FastAPI | 0.110+ | Framework web / API REST |
| Uvicorn | 0.29+ | Servidor ASGI para FastAPI |
| Pydantic v2 | 2.0+ | Validação de schemas de entrada e saída |
| pandas | 2.0+ | Manipulação de séries temporais |
| numpy | 1.26+ | Cálculos matemáticos e estatísticos |
| statsmodels | 0.14+ | Implementação do Holt-Winters (ExponentialSmoothing) |
| prophet | 1.1+ | Implementação do Prophet (Meta) |
| scikit-learn | 1.4+ | Métricas de avaliação (MAE, RMSE) e utilitários |
| pytest | 8.0+ | Testes unitários e de integração |
| pytest-asyncio | 0.23+ | Suporte a testes assíncronos FastAPI |
| httpx | 0.27+ | Cliente HTTP para testes de endpoints |
| python-dotenv | 1.0+ | Leitura de variáveis de ambiente (.env) |

### requirements.txt obrigatório
```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.0.0
pandas>=2.0.0
numpy>=1.26.0
statsmodels>=0.14.0
prophet>=1.1.0
scikit-learn>=1.4.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

---

## 3. Estrutura de Pastas

```
ml-service/
├── main.py                          ← entrypoint: instancia FastAPI, registra routers
├── requirements.txt
├── .env.example                     ← variáveis de ambiente documentadas (sem valores reais)
├── Dockerfile
│
└── app/
    ├── __init__.py
    │
    ├── routers/
    │   ├── __init__.py
    │   ├── predict_router.py        ← POST /predict
    │   └── health_router.py         ← GET /health
    │
    ├── services/
    │   ├── __init__.py
    │   ├── prediction_service.py    ← orquestra os modelos e seleciona o melhor
    │   ├── holt_winters_service.py  ← implementação isolada do Holt-Winters
    │   ├── prophet_service.py       ← implementação isolada do Prophet
    │   ├── abc_service.py           ← cálculo da Classificação ABC
    │   └── stock_service.py         ← cálculo de estoque de segurança, ponto de reposição, dias até ruptura
    │
    ├── models/
    │   ├── __init__.py
    │   ├── predict_request.py       ← schema Pydantic de entrada (POST /predict)
    │   └── predict_response.py      ← schema Pydantic de saída
    │
    └── tests/
        ├── __init__.py
        ├── test_predict_router.py
        ├── test_holt_winters_service.py
        ├── test_prophet_service.py
        ├── test_stock_service.py
        └── test_abc_service.py
```

**Regra:** cada arquivo tem uma única responsabilidade. Nunca misture lógica de modelo com lógica de rota.

---

## 4. Schemas Pydantic (Entrada e Saída)

### Request — `app/models/predict_request.py`

```python
from pydantic import BaseModel, Field
from datetime import date

class VendaDiaria(BaseModel):
    data: date
    quantidade: int = Field(gt=0)

class PredictRequest(BaseModel):
    produto_id: int
    historico: list[VendaDiaria] = Field(min_length=90)  # mínimo 90 registros
    lead_time_medio: int = Field(default=3, ge=1)
    variabilidade_lead_time: float = Field(default=1.0, ge=0)
    nivel_servico_alvo: float = Field(default=0.95, ge=0.5, le=0.999)
    estoque_atual: int = Field(ge=0)
    is_promocional: list[int] = Field(default=[])  # para Prophet
```

### Response — `app/models/predict_response.py`

```python
from pydantic import BaseModel
from datetime import date

class MetricasModelo(BaseModel):
    mape: float
    rmse: float
    mae: float

class PrevisaoDiaria(BaseModel):
    data: date
    quantidade_prevista: float

class PredictResponse(BaseModel):
    produto_id: int
    modelo_selecionado: str           # "holt_winters" ou "prophet"
    previsoes: list[PrevisaoDiaria]   # próximos 30 dias
    metricas: dict[str, MetricasModelo]  # comparativo dos dois modelos
    ponto_reposicao: float
    estoque_seguranca: float
    dias_ate_ruptura: float
    classe_abc: str                   # "A", "B" ou "C"
```

---

## 5. Arquitetura dos Services

### Fluxo obrigatório dentro de `prediction_service.py`

```
PredictRequest
      │
      ▼
1. Validar e preparar série temporal (pandas DataFrame)
      │
      ▼
2. Treinar Holt-Winters → MetricasModelo (MAPE, RMSE, MAE)
      │
3. Treinar Prophet      → MetricasModelo (MAPE, RMSE, MAE)
      │
      ▼
4. Comparar modelos → selecionar pelo menor MAPE
      │
      ▼
5. Gerar previsão dos próximos 30 dias com o modelo vencedor
      │
      ▼
6. Calcular: estoque de segurança, ponto de reposição, dias até ruptura
      │
      ▼
7. Calcular classe ABC (requer faturamento — usar quantidade se valor_venda ausente)
      │
      ▼
PredictResponse
```

### Regra de isolamento dos services

Cada service de modelo (`holt_winters_service.py`, `prophet_service.py`) deve expor **apenas uma função pública**:

```python
def treinar_e_avaliar(serie: pd.Series) -> tuple[MetricasModelo, pd.Series]:
    """
    Recebe uma série temporal de vendas diárias.
    Retorna as métricas de avaliação e a série de previsão para os próximos 30 dias.
    """
```

O `prediction_service.py` chama os dois e decide qual usar. Ele não conhece os detalhes internos de nenhum modelo.

---

## 6. Implementação dos Modelos

### Holt-Winters (`holt_winters_service.py`)

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Configuração recomendada para séries de varejo semanal:
model = ExponentialSmoothing(
    serie,
    trend="add",           # tendência aditiva
    seasonal="add",        # sazonalidade aditiva
    seasonal_periods=7,    # ciclo semanal (padrão do varejo de bairro)
    initialization_method="estimated"
)
```

**Atenção:** séries com menos de 2 ciclos completos (< 14 dias) não suportam sazonalidade. Implemente fallback para `seasonal=None` nesses casos, com log de aviso.

### Prophet (`prophet_service.py`)

```python
from prophet import Prophet

# Configuração recomendada para o contexto:
model = Prophet(
    yearly_seasonality=False,   # desabilitar: 90 dias não capturam ciclo anual
    weekly_seasonality=True,    # habilitar: padrão semanal do varejo
    daily_seasonality=False,    # desabilitar: granularidade diária já está na série
    interval_width=0.95         # intervalo de confiança alinhado ao nível de serviço
)
# Adicionar regressor promocional se is_promocional disponível:
model.add_regressor("is_promocional")
```

**Atenção:** Prophet exige DataFrame com colunas `ds` (date) e `y` (quantidade). Sempre renomear antes de passar.

### Cálculo de Métricas

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Usar validação walk-forward (time series split) — nunca split aleatório
# Treinar nos primeiros 80% da série, avaliar nos últimos 20%

mape = np.mean(np.abs((real - previsto) / real)) * 100
rmse = np.sqrt(mean_squared_error(real, previsto))
mae  = mean_absolute_error(real, previsto)
```

**Nunca usar `train_test_split` do scikit-learn em séries temporais** — ele embaralha os dados e invalida qualquer avaliação temporal.

---

## 7. Fórmulas dos KPIs de Estoque (`stock_service.py`)

```python
import numpy as np
from scipy import stats

def calcular_z_score(nivel_servico: float) -> float:
    """Converte nível de serviço em Z-score. Ex: 0.95 → 1.645"""
    return stats.norm.ppf(nivel_servico)

def calcular_estoque_seguranca(
    z: float,
    lead_time_medio: int,
    desvio_demanda: float,
    demanda_media: float,
    variabilidade_lead_time: float
) -> float:
    """
    Fórmula de Ballou (2006):
    ES = Z * sqrt(LT * σ²_demanda + demanda² * σ²_lead_time)
    """
    return z * np.sqrt(
        lead_time_medio * desvio_demanda**2 +
        demanda_media**2 * variabilidade_lead_time**2
    )

def calcular_ponto_reposicao(
    demanda_media: float,
    lead_time_medio: int,
    estoque_seguranca: float
) -> float:
    """PR = demanda_media_diária * lead_time + estoque_segurança"""
    return demanda_media * lead_time_medio + estoque_seguranca

def calcular_dias_ate_ruptura(
    estoque_atual: int,
    demanda_media_diaria: float
) -> float:
    """Quantos dias o estoque atual aguenta antes de atingir zero"""
    if demanda_media_diaria <= 0:
        return float("inf")
    return estoque_atual / demanda_media_diaria
```

---

## 8. Classificação ABC (`abc_service.py`)

```python
def classificar_abc(faturamento_total: float, faturamento_acumulado_percentual: float) -> str:
    """
    Classificação por representatividade no faturamento:
    A = top 80% do faturamento acumulado
    B = de 80% a 95%
    C = de 95% a 100%
    
    Nota: no MVP, se valor_venda não estiver disponível,
    usar quantidade vendida como proxy do faturamento.
    Documentar essa limitação na resposta.
    """
    if faturamento_acumulado_percentual <= 80:
        return "A"
    elif faturamento_acumulado_percentual <= 95:
        return "B"
    return "C"
```

---

## 9. Tratamento de Erros e Casos Especiais

Implemente tratamento explícito para todos os casos abaixo. **Nunca deixar exceção sem tratamento subir para o router.**

| Caso | Comportamento esperado |
|---|---|
| Histórico < 90 dias | Retornar HTTP 422 com mensagem clara: "Mínimo de 90 dias de histórico necessário" |
| Série com zeros excessivos (> 30% dos dias) | Log de aviso + continuar com fallback |
| Prophet falha (dados insuficientes) | Usar apenas Holt-Winters, registrar no response qual modelo foi descartado |
| Holt-Winters falha | Usar apenas Prophet, idem |
| Ambos falham | Retornar HTTP 500 com mensagem descritiva |
| MAPE > 50% no modelo vencedor | Incluir campo `aviso` no response: "Acurácia baixa — previsões com confiança reduzida" |
| `demanda_media_diaria = 0` | `dias_ate_ruptura = null`, não dividir por zero |
| `valor_venda` ausente na série | Usar `quantidade` como proxy para ABC, incluir campo `abc_proxy: true` no response |

---

## 10. Endpoint `/predict` — Router

```python
# app/routers/predict_router.py

from fastapi import APIRouter, HTTPException
from app.models.predict_request import PredictRequest
from app.models.predict_response import PredictResponse
from app.services.prediction_service import executar_previsao

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    """
    Recebe histórico de vendas de um produto e retorna previsão de demanda,
    KPIs de estoque e métricas comparativas dos modelos.
    """
    try:
        return await executar_previsao(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Log interno — nunca vazar stack trace para o cliente
        raise HTTPException(status_code=500, detail="Erro interno no motor preditivo")
```

---

## 11. Variáveis de Ambiente

```env
# .env.example
APP_ENV=development          # development | production
LOG_LEVEL=INFO               # DEBUG | INFO | WARNING | ERROR
ML_SERVICE_PORT=8000
```

Carregar com `python-dotenv` no `main.py`. Nunca hardcodar valores.

---

## 12. Padrão de Logging

```python
import logging

logger = logging.getLogger(__name__)

# Usar em todo service:
logger.info(f"[produto_id={produto_id}] Iniciando previsão")
logger.info(f"[produto_id={produto_id}] Holt-Winters MAPE={mape_hw:.2f}% | Prophet MAPE={mape_prophet:.2f}%")
logger.info(f"[produto_id={produto_id}] Modelo selecionado: {modelo_selecionado}")
logger.warning(f"[produto_id={produto_id}] Prophet descartado: {motivo}")
logger.error(f"[produto_id={produto_id}] Falha no motor: {str(e)}")
```

Sempre incluir `produto_id` nos logs para rastreabilidade.

---

## 13. Testes

### Cobertura mínima obrigatória

| Arquivo | O que testar |
|---|---|
| `test_holt_winters_service.py` | Série normal, série com zeros, série curta (< 14 dias) |
| `test_prophet_service.py` | Série normal, série sem coluna promocional |
| `test_stock_service.py` | Fórmulas de ES, PR e ruptura com valores conhecidos |
| `test_abc_service.py` | Classificação A, B e C com percentuais limítrofes |
| `test_predict_router.py` | POST /predict com payload válido, com < 90 dias, com série inválida |

### Como rodar os testes

```bash
# Na raiz do ml-service:
pytest app/tests/ -v --tb=short
```

### Fixtures reutilizáveis

Criar `conftest.py` dentro de `app/tests/` com fixtures de série temporal para reutilizar em todos os testes:

```python
# app/tests/conftest.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def serie_90_dias():
    """Série temporal sintética com 90 dias de dados diários."""
    datas = pd.date_range(start="2025-01-01", periods=90, freq="D")
    quantidades = np.random.randint(5, 30, size=90)
    return pd.Series(quantidades, index=datas)

@pytest.fixture
def payload_valido():
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
        "estoque_atual": 40
    }
```

---

## 14. Dockerfile do ml-service

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 15. O que NÃO fazer

- ❌ Nunca usar `train_test_split` do scikit-learn em séries temporais — embaralha os dados e invalida a avaliação
- ❌ Nunca deixar uma exceção sem tratamento subir para o router sem ser capturada
- ❌ Nunca vazar stack trace Python para o cliente — log interno, mensagem amigável para fora
- ❌ Nunca aceitar histórico com menos de 90 dias — rejeitar com HTTP 422 e mensagem clara
- ❌ Nunca dividir por zero no cálculo de dias até ruptura — tratar `demanda_media = 0` explicitamente
- ❌ Nunca hardcodar parâmetros dos modelos (seasonal_periods, interval_width) fora dos services
- ❌ Nunca colocar lógica de modelo dentro do router — router só roteia, service processa
- ❌ Nunca renomear as colunas do Prophet dentro do prediction_service — isso é responsabilidade do prophet_service
- ❌ Nunca commitar arquivo `.env` com valores reais — apenas `.env.example`

---

## 16. Referências Técnicas

- HYNDMAN, R.J.; ATHANASOPOULOS, G. *Forecasting: Principles and Practice.* 3. ed. OTexts, 2021. *(Holt-Winters, métricas de avaliação, walk-forward validation)*
- TAYLOR, S.J.; LETHAM, B. Forecasting at scale. *The American Statistician*, 72(1), 2018. *(Prophet)*
- BALLOU, Ronald H. *Gerenciamento da cadeia de suprimentos.* 5. ed. Bookman, 2006. *(Estoque de Segurança — fórmula de Ballou)*

---

*Atualizar este arquivo sempre que houver mudança de biblioteca, novo modelo adicionado ou alteração nas fórmulas dos KPIs.*
