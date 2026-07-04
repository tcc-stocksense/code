# SESSION.md — StockSense

## Cabeçalho do Projeto

| Campo | Valor |
|---|---|
| **Nome** | StockSense — Motor de Otimização Preditiva de Estoque |
| **Tipo** | TCC — Sistemas de Informação (2026) |
| **Repositório** | Monorepo: `backend/`, `ml-service/`, `frontend/` |
| **Stack** | Kotlin/Spring Boot · Python/FastAPI · MySQL 8 · HTML/CSS/JS |
| **Branch principal** | `main` |
| **Branches abertas** | `feat/auth-login-jwt`, `feat/motor-abc`, `test/importacao-services` (todas pushed, sem PR) |

> **Ordem de merge das branches abertas:** `feat/auth-login-jwt` (Épico 1) →
> `feat/motor-abc` (Épico 3) → `test/importacao-services` (Épico 2 testes/doc).
> O Motor depende do Spring Security do Épico 1, então a `feat/auth-login-jwt`
> **precisa ser mergeada antes** da `feat/motor-abc`. A `test/importacao-services`
> é independente (base `main` limpa) e pode ir a qualquer momento.

---

## Última Sessão — 2026-07-04

### O que foi desenvolvido

#### backend (Kotlin/Spring Boot) — branch `feat/motor-abc`

Implementação completa do **Épico 3 — Motor Preditivo + Curva ABC (T-18 a T-25)**.
Entrega `POST /api/motor/recalcular`, que aciona o ml-service por produto, persiste
previsões e métricas, atualiza os KPIs de estoque e recalcula a classificação ABC.

| Arquivo | O que foi criado/alterado |
|---|---|
| `domain/Previsao.kt`, `domain/MetricaModelo.kt` | **CRIADOS** — mapeiam as tabelas do `V1` |
| `repository/PrevisaoRepository.kt`, `MetricaModeloRepository.kt` | **CRIADOS** |
| `domain/Produto.kt` | + campo `estabelecimentoId` (coluna já existia no `V1`) |
| `repository/ProdutoRepository.kt` | + `findByEstabelecimentoId` |
| `repository/VendaRepository.kt` | + `agregarVendasDiarias` (SUM por dia) e `agregarFaturamentoPorProduto` (ABC) |
| `client/dto/PredictRequest.kt`, `PredictResponse.kt` | **CRIADOS** — contrato Feign espelhando o Pydantic; snake_case via `@JsonNaming` |
| `client/MlServiceClient.kt` | **CRIADO** — `@FeignClient` predict/health |
| `service/MotorService.kt` | **CRIADO** — agrega vendas por dia, chama o motor, persiste tudo numa transação por produto |
| `service/AbcService.kt` | **CRIADO** — ranking 80/95%, primeiro produto sempre A, fallback por quantidade |
| `controller/MotorController.kt` | **CRIADO** — lote com transação isolada por produto |
| `dto/response/MotorRecalculoResponse.kt` | **CRIADO** |
| `test/.../MotorServiceTest.kt`, `AbcServiceTest.kt` | **CRIADOS** — 7 testes, todos passando |

**Validação em runtime (não só testes):** o backend subiu contra o MySQL real
(`ddl-auto: validate` OK para as novas entidades) e as três queries JPQL foram
exercitadas — inclusive a `agregarVendasDiarias` com `CAST(... AS date)`, via um
produto seedado (o ABC classificou como `A` e persistiu no banco). O único caminho
não exercitado é uma chamada **bem-sucedida** ao ml-service (precisa do serviço Python
no ar + 90 dias de dados) — coberto pelos testes unitários.

#### Divergências código × arquitetura encontradas (registradas)

- O ml-service **ainda devolve `classe_abc` e `abc_proxy`** no `PredictResponse`, apesar
  da ADR #3 (ABC migrou para o backend). O backend os **ignora**
  (`@JsonIgnoreProperties`) e calcula ABC no `AbcService`. Dívida técnica do ml-service.
- O ml-service **não devolve `desvio_padrao_demanda`** (calcula e descarta) — confirma a
  pendência **T-05**. Fora do contrato Feign por ora; bloqueia só a T-30 (Épico 4).
- O `_preparar_serie` do ml-service **não agrupa por dia** → o `MotorService` agrega as
  vendas por data (SUM) antes de enviar.

### Decisões técnicas tomadas nesta sessão

| Decisão | Motivo |
|---|---|
| `feat/motor-abc` baseada em `feat/auth-login-jwt`, não em `main` | O Épico 3 usa o Spring Security e a `RecursoNaoEncontradoException` do Épico 1, que ainda não estão na `main` |
| Adicionar `estabelecimentoId` à entidade `Produto` agora | Pré-requisito real do ABC e do controller (filtro por estabelecimento); a coluna já existia no `V1` |
| Lead time no default (3 / 1.0) | `ProdutoFornecedor` ainda não existe — comportamento documentado no Guia de Importação |
| Backend ignora `classe_abc` do motor e calcula ABC próprio | Segue a ADR #3, mesmo com o ml-service ainda devolvendo o campo |
| Transação por produto (proxy) no lote do controller | Falha de um produto não aborta o recálculo dos demais |

#### Sobras do Épico 2 — branch `test/importacao-services`

Fechamento do núcleo do Épico 2 (Importação), independente da pilha auth/motor
(o código de importação já estava na `main`):

- **T-17 — testes de importação** (13, todos passando): `ProdutoImportacaoServiceTest` (6)
  e `VendaImportacaoServiceTest` (7), construindo planilhas `.xlsx` reais em memória com
  Apache POI + `MockMultipartFile`. Cobrem planilha válida, `produto_id` duplicado, coluna
  obrigatória ausente, estoque negativo, campo calculado, arquivo não-`.xlsx`, produto
  inexistente, data inválida, `quantidade ≤ 0`, `valor_venda` com vírgula, histórico < 90 dias.
- **`backend/CLAUDE.md`** atualizado (§5 + tabela de endpoints) para refletir os **dois
  endpoints reais** (`/api/importacao/produtos` e `/vendas`). ⚠️ Essa mudança está **só na
  branch** `test/importacao-services` — a `main` ainda descreve 1 endpoint até o merge.
- **`tasks.md`**: Épico 2 (T-12 a T-17) marcado conforme o implementado.
- **Fora do escopo (deliberado):** `Fornecedor`/`ProdutoFornecedor` (MVP-opcional) — habilitaria
  o lead time real no Motor (hoje no default 3/1.0).

### Status do backend ao final desta sessão

- **Épico 1 (Auth):** completo na `feat/auth-login-jwt` (pushed, PR não aberta).
- **Épico 2 (Importação):** núcleo + testes (T-17) prontos; testes/doc na branch
  `test/importacao-services` (pushed, PR não aberta). Falta só `Fornecedor`/`ProdutoFornecedor`
  (MVP-opcional). `estabelecimentoId` do `Produto` adicionado via Épico 3.
- **Épico 3 (Motor + ABC):** completo na `feat/motor-abc` (pushed, PR não aberta).
- **Épicos 4–6 e Pós-MVP:** não iniciados. T-27 (detalhe do produto) bloqueado por T-05.
- **ml-service e frontend:** sem mudanças nesta sessão.

**Três branches abertas** (todas pushed, sem PR): `feat/auth-login-jwt`, `feat/motor-abc`
(depende da auth), `test/importacao-services` (base `main` limpa). Ordem de merge:
auth → motor → importacao.

---

## Sessão — 2026-07-03 (Auth / JWT)

### O que foi desenvolvido

#### backend (Kotlin/Spring Boot) — branch `feat/auth-login-jwt`

Auditoria completa do `backend/tasks.md` contra o código já existente (estava
desatualizado, dizia "zero código Kotlin implementado" quando o Épico 2 já tinha
núcleo pronto). Depois, implementação completa do **Épico 1 — Auth/Login (T-06 a T-11)**:

| Arquivo | O que foi criado/alterado |
|---|---|
| `build.gradle.kts` | + `spring-boot-starter-security`, `jjwt-api/impl/jackson:0.12.6`, `spring-security-test` |
| `application.yml` | + `jwt.secret` e `jwt.expiration-ms` (via env var) |
| `domain/Estabelecimento.kt` | **CRIADO** — entidade de login (id, nomeFantasia, cnpj, endereco, email, senhaHash) |
| `repository/EstabelecimentoRepository.kt` | **CRIADO** — `findByEmail` |
| `exception/RecursoNaoEncontradoException.kt` | **CRIADO** + handler no `GlobalExceptionHandler` (404) |
| `config/JwtConfig.kt` | **CRIADO** — `@ConfigurationProperties(prefix = "jwt")` |
| `service/JwtService.kt` | **CRIADO** — gerar/validar/extrair token (subject = estabelecimentoId) |
| `dto/request/LoginRequest.kt`, `dto/response/LoginResponse.kt` | **CRIADOS** |
| `service/AuthService.kt` | **CRIADO** — valida BCrypt, mesma exceção p/ email não encontrado ou senha errada |
| `config/JwtAuthFilter.kt` + `config/SecurityConfig.kt` | **CRIADOS** — libera só `/api/auth/login`, resto exige Bearer token |
| `controller/AuthController.kt` | **CRIADO** — `POST /api/auth/login` |
| `test/.../AuthServiceTest.kt` | **CRIADO** — 3 cenários com MockK, todos passando |
| `V2__seed_dados_padrao.sql` | Placeholder de `senha_hash` trocado por hash BCrypt de credencial de dev (`admin@stocksense.local` / `admin123`) — decisão explícita do time, diferente do padrão "nunca commitar hash real" |

Testado localmente: `POST /api/auth/login` retorna `200` com JWT válido; endpoint
protegido (`/api/importacao/produtos`) retorna `403` sem token e passa da
autenticação com token válido.

`tasks.md` (T-01 a T-11, exceto T-02/T-05 parciais) foi auditado/atualizado e
commitado direto na `main`; o código do Épico 1 foi para a branch
`feat/auth-login-jwt` (push feito, PR ainda não aberta).

`backend/CLAUDE.md` ganhou uma seção **"Como rodar o backend localmente"** —
commitada na `main`.

#### Setup local (troubleshooting resolvido nesta sessão)

- Existe um `.env` na **raiz do monorepo** com credenciais próprias do MySQL
  (`DB_USERNAME=stocksense`, `DB_PASSWORD=5505`) — diferentes dos defaults do
  `docker-compose.yml` (`appuser`/`apppassword`) e do `application.yml` (`root`/`root`).
  Sempre checar esse `.env` antes de rodar o backend fora do compose.
- O volume `code_db_data` tinha uma versão pré-consolidação da `V1` aplicada,
  causando `Migration checksum mismatch` no Flyway. Resolvido com
  `docker-compose down -v && docker-compose up -d db` (recria o volume do zero).

### Decisões técnicas tomadas nesta sessão

| Decisão | Motivo |
|---|---|
| Pular T-03 (SecurityConfig temporário) e ir direto pra T-09 (definitivo) | Épico 1 foi implementado de uma vez só — não fazia sentido criar uma config pra substituir minutos depois |
| Importação usa 2 endpoints (`/api/importacao/produtos`, `/api/importacao/vendas`) em vez de 1 único `/api/importacao` | Decisão explícita do time, diverge do CLAUDE.md original — **CLAUDE.md do backend ainda não foi atualizado pra refletir isso** |
| `senha_hash` do seed padrão passou a ser um hash BCrypt real de dev (`admin123`), não mais um placeholder inválido | Facilita testar login localmente sem precisar abrir o banco manualmente — nunca deve ir para ambiente compartilhado |
| Todo o resto dos endpoints exige JWT (`anyRequest().authenticated()`) | Segue T-09 à risca — consequência: `/api/importacao/*` agora exige token, antes estava aberto |

### Status do backend ao final desta sessão

- **Épico 0 (Fundação):** T-01, T-02, T-04 feitos; T-03 pulado deliberadamente; T-05
  (acordo `desvio_padrao_demanda` com o ml-service) ainda pendente de decisão.
- **Épico 1 (Auth):** T-06 a T-11 completos, testados localmente, na branch
  `feat/auth-login-jwt` (pushed, PR não aberta).
- **Épico 2 (Importação):** núcleo já existia antes desta sessão, sem mudanças de
  código aqui — falta T-17 (testes), `Fornecedor`/`ProdutoFornecedor` (MVP-opcional)
  e o campo `estabelecimentoId` em `Produto`.
- **Épicos 3–6 e Pós-MVP:** não iniciados.
- **ml-service e frontend:** sem mudanças nesta sessão — ver seção anterior abaixo.

---

## Sessão anterior — 2026-05-18

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
| Migrations V2, V3, V4 | ✅ Existem | Criadas em commit `3fef6bc` — V1 (schema), V2 (seed padrão), V3 (add estabelecimento_id), V4 (add índices). **Consolidadas depois em uma única `V1` + `V2` de seed** (ver commits mais recentes) |
| ml-service executado localmente | ⚠️ Parcial | Servidor não foi levantado; testes rodaram via TestClient |
| Branch `feat/ml-service-motor-preditivo` | ✅ Mergeada | Mergeada na `main` via PR #3 |
| Código Kotlin no backend | ✅ Em andamento | Épico 2 (Importação) e Épico 1 (Auth) já implementados — ver sessão 2026-07-03 acima |
| PR de `feat/auth-login-jwt` (Épico 1) | ⚠️ Pendente | Branch pushed, falta abrir e mergear — **mergear antes** da motor-abc |
| PR de `feat/motor-abc` (Épico 3) | ⚠️ Pendente | Branch pushed, falta abrir e mergear — **depende da auth-login-jwt** |
| PR de `test/importacao-services` (Épico 2 testes/doc) | ⚠️ Pendente | Branch pushed, falta abrir e mergear — independente, base `main` limpa |
| T-05 — acordo `desvio_padrao_demanda` no `PredictResponse` | ⚠️ Pendente | Confirmado: o ml-service não devolve. Bloqueia T-27 (detalhe do produto, Épico 4) |
| ml-service ainda devolve `classe_abc`/`abc_proxy` | ⚠️ Dívida técnica | ABC migrou pro backend (ADR #3); backend ignora, mas o campo deveria sair do ml-service |
| T-17 — testes unitários de importação | ✅ Feito | 13 testes na `test/importacao-services`, todos passando |
| `estabelecimentoId` ausente na entidade `Produto` | ✅ Resolvido | Adicionado na `feat/motor-abc` (Épico 3) |
| CLAUDE.md do backend sobre `/api/importacao` | ✅ Corrigido na branch | Atualizado para 2 endpoints na `test/importacao-services`; chega na `main` no merge |
| Fornecedor / ProdutoFornecedor (MVP-opcional) | ❌ Não feito | Sem essas entidades, o lead time do Motor cai sempre no default (3 / 1.0) |

---

## Próxima Sessão — Fazer nesta ordem

> Atualizado em 2026-07-04.

### Passo 1: Mergear as branches abertas na ordem certa

- Abrir e mergear a PR de `feat/auth-login-jwt` (Épico 1) na `main`.
- Depois abrir e mergear a PR de `feat/motor-abc` (Épico 3) na `main`.

### Passo 2: Fechar o Épico 2 (Importação)

- T-17 — testes unitários de `ProdutoImportacaoService` e `VendaImportacaoService`.
- Atualizar o `CLAUDE.md` do backend para refletir os 2 endpoints de importação
  (`/api/importacao/produtos`, `/api/importacao/vendas`) em vez do único
  `/api/importacao` descrito hoje.
- Avaliar se vale implementar `Fornecedor`/`ProdutoFornecedor` agora (habilita o
  lead time real no Motor, hoje no default).

### Passo 3: Épico 4 — Produto (T4 + T6 + T10)

- `ProdutoService` (listagem, edição de estoque, detalhe), `MetricaService`
  (comparativo Holt-Winters × Prophet), `ProdutoController`.
- ⚠️ T-30 (detalhe do produto) depende de resolver **T-05** (`desvio_padrao_demanda`).

### Backlog antigo do ml-service (ainda não resolvido, sem mudanças nesta sessão)

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

### Passo 5: Merge da branch e início do backend Kotlin (✅ já feito — ver sessão 2026-07-03 no topo)

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
