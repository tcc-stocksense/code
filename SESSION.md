# SESSION.md — StockSense

## Cabeçalho do Projeto

| Campo | Valor |
|---|---|
| **Nome** | StockSense — Motor de Otimização Preditiva de Estoque |
| **Tipo** | TCC — Sistemas de Informação (2026) |
| **Repositório** | Monorepo: `backend/`, `ml-service/`, `frontend/` |
| **Stack** | Kotlin/Spring Boot · Python/FastAPI · MySQL 8 · HTML/CSS/JS |
| **Branch principal** | `main` |
| **Branch de desenvolvimento atual** | `feat/ml-service-motor-preditivo` (não mergeada) |

---

## Última Sessão — 2026-05-18

### O que foi desenvolvido

#### ml-service (Python/FastAPI) — branch `feat/ml-service-motor-preditivo`

9 commits organizados e publicados no GitHub:

| Commit | O que foi criado |
|---|---|
| `36499e9` | Schemas Pydantic: `PredictRequest`, `PredictResponse`, `VendaDiaria`, `MetricasModelo`, `PrevisaoDiaria` |
| `c5126e6` | Endpoints `GET /health` e `POST /predict` + `main.py` + `requirements.txt` |
| `3340e8b` | `holt_winters_service.py` — Holt-Winters com walk-forward 80/20, fallback sem sazonalidade |
| `de5acef` | `prophet_service.py` — Prophet com sazonalidade semanal configurável, ds/y isolado no serviço |
| `a0c6dca` | `stock_service.py` — Z-score, estoque de segurança (Ballou), ponto de reposição, dias até ruptura |
| `0135014` | `abc_service.py` — Classificação A/B/C com fallback por quantidade quando `valor_venda` ausente |
| `a36d8dd` | `prediction_service.py` — Orquestrador: treina os dois modelos, seleciona pelo menor MAPE, calcula KPIs |
| `d143559` | Testes unitários: `conftest.py` + 5 arquivos `test_*.py` cobrindo todos os services |
| `5f9d3fb` | `generate_synthetic_data.py` — gerador de dados com sazonalidade semanal realista |

#### Correção de bug nesta sessão

- **`abc_service.py`** — produto único estava sendo classificado como `C` (100% acumulado)
  em vez de `A`. Corrigido com early return: produto único sempre recebe classe `A`.

#### Diagnóstico de testes

Testes rodados com `pytest app/tests/ -v`:

| Arquivo de teste | Status |
|---|---|
| `test_stock_service.py` | ✅ Todos passando |
| `test_abc_service.py` | ✅ Todos passando (após correção do bug) |
| `test_holt_winters_service.py` | ✅ Todos passando |
| `test_predict_router.py` | ✅ Todos passando |
| `test_prophet_service.py` | ❌ 11 falhas — CmdStan não instalado no Windows |

### Decisões técnicas tomadas

| Decisão | Motivo |
|---|---|
| Comunicação Spring Boot → FastAPI via OpenFeign síncrono | Motor preditivo deve responder dentro de 30s; simplicidade supera complexidade assíncrona no MVP |
| Seleção de modelo pelo menor MAPE | Métrica interpretável para o contexto de varejo; RMSE e MAE disponíveis para análise secundária |
| Walk-forward 80/20 (nunca `train_test_split`) | Séries temporais exigem divisão cronológica; split aleatório invalida a avaliação |
| Fallback sem sazonalidade quando série < 14 dias | statsmodels e Prophet exigem pelo menos 2 ciclos completos para sazonalidade semanal |
| Produto único na ABC sempre recebe classe A | Um único produto É o mais importante por definição; 100% acumulado não deve significar classe C |
| `nivel_servico_alvo` vem do cadastro do produto (padrão 0.95) | CLAUDE.md proíbe hardcodar este parâmetro |
| MySQL usa `DATETIME`, não `TIMESTAMP` | `TIMESTAMP` tem limitação de fuso horário no MySQL |
| Migrations com Flyway (prefixo `V1__`, `V2__`...) | Nunca alterar migration já commitada — sempre criar nova |

### Arquivos criados ou modificados relevantes

```
ml-service/
├── main.py                          ← modificado: registra health_router e predict_router
├── requirements.txt                 ← modificado: dependências fixadas com versões exatas
└── app/
    ├── models/
    │   ├── predict_request.py       ← CRIADO
    │   └── predict_response.py      ← CRIADO
    ├── routers/
    │   ├── health_router.py         ← CRIADO
    │   └── predict_router.py        ← CRIADO
    ├── services/
    │   ├── holt_winters_service.py  ← CRIADO
    │   ├── prophet_service.py       ← CRIADO
    │   ├── stock_service.py         ← CRIADO
    │   ├── abc_service.py           ← CRIADO (+ bug corrigido nesta sessão)
    │   └── prediction_service.py    ← CRIADO
    └── tests/
        ├── conftest.py              ← CRIADO
        ├── generate_synthetic_data.py ← CRIADO
        ├── test_holt_winters_service.py ← CRIADO
        ├── test_prophet_service.py  ← CRIADO
        ├── test_stock_service.py    ← CRIADO
        ├── test_abc_service.py      ← CRIADO
        └── test_predict_router.py   ← CRIADO
```

### Status atual de cada serviço

#### ml-service
- **Existe:** estrutura completa, todos os services, modelos Pydantic, routers, testes unitários, gerador de dados sintéticos
- **Branch:** `feat/ml-service-motor-preditivo` — **não mergeada no `main`**
- **Falta:**
  - Resolver CmdStan no Windows (ver seção Pendente)
  - Rodar `POST /predict` com dados reais e validar métricas
  - Criar `generate_report.py` (script de relatório PDF)
  - Merge da branch para `main`

#### backend (Kotlin/Spring Boot)
- **Existe:** estrutura de pacotes (`controller`, `service`, `repository`, `client`, `dto`, `config`, `exception`, `domain`), `application.yml`, migrations V1–V4
- **Falta:** TODO o código Kotlin — nenhum arquivo `.kt` criado ainda
  - Entidades JPA (`Produto`, `Venda`, `Previsao`, `Estabelecimento`, `Fornecedor`, `PerdaEstoque`)
  - Repositories Spring Data
  - Services de negócio
  - Controllers REST com validação Bean Validation
  - Feign Client (`MlServiceClient`) apontando para `${ML_SERVICE_URL}`
  - Parser/validador de planilhas XLSX
  - Agendamento mensal via `@Scheduled`

#### frontend (HTML/CSS/JS)
- **Existe:** `index.html`, `dashboard.html`, `importacao.html`, `relatorios.html`, `main.css`, `main.js`, `dashboard.js`, `importacao.js`, `relatorios.js`
- **Falta:** integração real com a API (atualmente sem chamadas HTTP ao backend), lógica do semáforo de alertas, curva ABC interativa, upload de planilha funcional

---

## Pendente e Bugs Conhecidos

| Item | Status | Observação |
|---|---|---|
| Prophet: CmdStan não instalado no Windows | ❌ Bloqueado | `mingw32-make` não encontrado. Instalar Rtools: `winget install -e --id RProject.Rtools`, adicionar `C:\rtools44\mingw64\bin` ao PATH, depois `python -m cmdstanpy.install_cmdstan` |
| Testes do `test_prophet_service.py` | ❌ 11 falhas | Dependem da resolução do CmdStan acima |
| `generate_report.py` | ❌ Não existe | Precisa ser criado; deve gerar PDF com gráficos de acurácia dos modelos |
| Migrations V2, V3, V4 | ✅ Existem | Criadas em commit `3fef6bc` — V1 (schema), V2 (seed padrão), V3 (add estabelecimento_id), V4 (add índices) |
| ml-service executado localmente | ⚠️ Parcial | Servidor não foi levantado; testes rodaram via TestClient |
| Branch `feat/ml-service-motor-preditivo` | ⚠️ Pendente | Não mergeada no `main` — fazer merge após validar localmente |
| Código Kotlin no backend | ❌ Não iniciado | Próxima grande fase do projeto |

---

## Próxima Sessão — Fazer nesta ordem

### Passo 1: Resolver CmdStan e rodar o ml-service localmente

```powershell
# Instalar Rtools (inclui mingw32-make necessário para compilar CmdStan)
winget install -e --id RProject.Rtools

# Adicionar ao PATH (ajustar versão se necessário)
$env:PATH = "C:\rtools44\mingw64\bin;C:\rtools44\usr\bin;$env:PATH"

# Verificar que mingw32-make está disponível
mingw32-make --version

# Com o venv ativado, instalar CmdStan
cd ml-service
.\venv\Scripts\Activate.ps1
python -m cmdstanpy.install_cmdstan

# Subir o servidor
uvicorn main:app --reload --port 8000
```

Verificar:
- `http://localhost:8000/health` → `{"status": "ok", "service": "ml-service"}`
- `http://localhost:8000/docs` → Swagger UI com os dois endpoints

### Passo 2: Rodar todos os testes

```powershell
# Com o venv ativado, na pasta ml-service
pytest app/tests/ -v --tb=short

# Se querer pular Prophet enquanto CmdStan não está instalado:
pytest app/tests/ -v -k "not prophet"
```

Meta: 100% passando antes de avançar.

### Passo 3: Fazer chamada real ao `/predict` com dados sintéticos

```powershell
# Gerar payload e chamar o endpoint (servidor deve estar rodando)
python app/tests/generate_synthetic_data.py

# Validar na resposta:
# - modelo_selecionado: "holt_winters" ou "prophet"
# - MAPE do vencedor < 50% (senão campo "aviso" aparece)
# - previsoes: lista com 30 entradas
# - ponto_reposicao, estoque_seguranca, dias_ate_ruptura: valores positivos
# - classe_abc: "A", "B" ou "C"
```

### Passo 4: Criar `generate_report.py`

Criar `ml-service/generate_report.py` com:
- Carregamento dos dados sintéticos via `generate_synthetic_data.py`
- Chamada ao `POST /predict`
- Geração de PDF com 4 páginas:
  1. Comparativo MAPE Holt-Winters vs Prophet
  2. Gráfico de previsão vs histórico real
  3. KPIs de estoque (ponto de reposição, estoque de segurança, dias até ruptura)
  4. Curva ABC

### Passo 5: Merge da branch e início do backend Kotlin

```bash
git checkout main
git merge feat/ml-service-motor-preditivo
git push origin main
```

Após o merge, iniciar o backend:
- Criar entidades JPA (`Produto`, `Venda`, `Previsao`, `Estabelecimento`)
- Implementar `MlServiceClient` com Feign Client
- Criar endpoint `POST /api/motor/executar`

---

## Como Retomar Esta Sessão

Cole exatamente este prompt na próxima abertura do Claude Code:

```
Leia o CLAUDE.md da raiz, o CLAUDE.md da pasta atual e o
SESSION.md antes de qualquer ação. Com base nesses arquivos
e no git log --oneline, me diga em que ponto estamos no
desenvolvimento do StockSense e confirme qual é o próximo
passo antes de começar.
```
