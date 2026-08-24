# Mapa do Projeto e Infraestrutura AWS — StockSense

> **StockSense · TCC 2026** — Documento de arquitetura de infraestrutura.
> Data: 2026-08-17 · Status: **arquitetura definida — pendente execução do deploy**

> ⚠️ **Como ler.** A **Parte 1** é o inventário do que existe hoje, auditado no código (não na
> documentação). A **Parte 2** lista os requisitos que o próprio código impõe à infraestrutura —
> cada um com a evidência que o origina. Da **Parte 3** em diante é o desenho da nuvem, já
> específico para AWS. Complementa `revisao-arquitetura.md` (fidelidade às decisões) e
> `relatorio-motor-assincrono.md` (carga do motor).

## Decisões que definem este documento

| Decisão | Escolha | Motivo |
|---|---|---|
| Provedor | **AWS** | única fonte de créditos do projeto |
| Orçamento | **~US$ 100 em créditos** | inviabiliza ALB (~US$ 18/mês só de taxa fixa) e ECS Fargate |
| Finalidade | **Demonstração para a banca** | sem exigência de 24/7, alta disponibilidade ou backup rígido |
| Computação | **1 instância EC2 t3.medium** rodando o `docker compose` | migração quase direta do ambiente que já funciona |
| Banco | **MySQL 8.0 em container na própria VM** | já configurado e testado; RDS consumiria metade do crédito |
| Backup | `mysqldump` diário → S3 + snapshot EBS antes da defesa | dados são reconstruíveis (ver §7.2) |

---

# PARTE 1 — Mapa do projeto

## 1.1 Visão geral

| Componente | Stack | Porta | Estado |
|---|---|---|---|
| `frontend/web` | HTML/CSS/JS puro (ES modules), nginx | 80 | 10 telas prontas, **camada mock ligada** — integração pendente |
| `backend` | Kotlin 1.9.25 · Spring Boot 3.3.4 · JVM 17 · Gradle | 8080 | Épicos 0–5 concluídos; Épico 7 (async) suspenso |
| `ml-service` | Python 3.10 · FastAPI · statsmodels · Prophet | 8000 | Funcional, 66 testes, Prophet operante desde 2026-07-24 |
| `db` | MySQL 8.0 (container) | 3307→3306 | 7 tabelas, migrations V1–V3 |

Fluxo: **navegador → backend → (ml-service | MySQL)**. O frontend nunca fala com o ml-service, e o
ml-service nunca toca o banco — as duas invariantes do `CLAUDE.md` §3.

## 1.2 Backend — inventário

| Camada | Arquivos |
|---|---|
| Controllers (7) | `Auth`, `Importacao`, `Produto`, `Motor`, `Alerta`, `Dashboard`, `Abc` |
| Services (10) | `Auth`, `Jwt`, `ProdutoImportacao`, `VendaImportacao`, `Produto`, `Motor`, `Abc`, `Alerta`, `Dashboard`, `Metrica` |
| Repositories (5) | `Estabelecimento`, `Produto`, `Venda`, `Previsao`, `MetricaModelo` |
| Domain (5) | mesmas 5 entidades JPA |
| Client | `MlServiceClient` (Feign) + `PredictRequest`/`PredictResponse` |
| Config | `SecurityConfig`, `JwtAuthFilter`, `JwtConfig` |
| Testes | 7 classes de service (~40 testes) |

**Dependências com peso de infraestrutura:** Spring Security + JJWT, Spring Cloud OpenFeign,
Flyway + `flyway-mysql` (migrations na subida), Apache POI 5.2.5 (parse de `.xlsx` em memória),
MySQL connector.

**Endpoints:** `/api/auth/login` (público), `/api/importacao/{produtos,vendas}`, `/api/produtos`,
`/api/produtos/{id}`, `PATCH /api/produtos/{id}/estoque`, `/api/motor/recalcular`, `/api/alertas`,
`/api/dashboard`, `/api/curva-abc`, `/api/metricas`. Tudo autenticado por JWT exceto o login
(`SecurityConfig.kt:24-25`).

## 1.3 ml-service — inventário

- **Rotas:** `GET /health` (sem auth), `POST /predict` (sem auth).
- **Services:** `holt_winters_service`, `prophet_service`, `prediction_service` (orquestra e
  seleciona por menor MAPE), `stock_service` (Ballou: Z, estoque de segurança, ponto de reposição,
  dias até ruptura).
- **Testes:** 66, 0 falhas.
- **Análise acadêmica:** `analysis/analise_modelos.ipynb` (28 células, 14 figuras) + `docs/` com os
  PDFs de relatório e capítulo de validação. **Não faz parte do runtime** — não deve ir para a
  imagem de produção.
- **Pin crítico:** `cmdstanpy==1.2.4` (T-12). Sem ele o Prophet quebra e o motor cai silenciosamente
  para Holt-Winters — o que invalidaria a comparação, núcleo acadêmico do TCC.

## 1.4 Frontend — inventário

10 páginas (`login`, `dashboard`, `estoque`, `produto-detalhe`, `importar`, `alertas`, `curva-abc`,
`comparativo-modelos`, `sugestao-compra`, `configuracoes`), 11 componentes JS, tokens de CSS.

**Dois pontos que travam o deploy:**
- `apiClient.js:8` — `const USAR_MOCK = localStorage.getItem('stocksense_mock') !== 'off'`. O mock é
  o **padrão**; o app só fala com a API se alguém desligar o mock no navegador.
- `config.js:1` — `API_BASE_URL = 'http://localhost:8080/api'`, hardcoded.

Ambos tratados na Parte 8.

## 1.5 Banco de dados

7 tabelas: `estabelecimento`, `produto`, `fornecedor`, `produto_fornecedor`, `venda`, `previsao`,
`metrica_modelo`. Migrations `V1` (schema, congelada), `V2` (seed), `V3` (`dias_ate_ruptura`).
`ddl-auto: validate` + Flyway `baseline-on-migrate: true`.

**Volumetria projetada** (312 SKUs, 1 estabelecimento):

| Tabela | Estimativa | Crescimento |
|---|---|---|
| `produto` | 312 linhas | estático |
| `venda` | 312 × ~365 dias ≈ **114 mil linhas/ano** | por importação |
| `previsao` | 312 × 30 = **9.360 linhas por execução** (append) | ~112 mil/ano no cron mensal |
| `metrica_modelo` | 312 × 2 = **624 linhas por execução** | ~7,5 mil/ano |

Ordem de grandeza: **bem abaixo de 1 GB mesmo em 3 anos**. O banco não é o gargalo — o
dimensionamento é ditado por CPU do ml-service, não por armazenamento. É também o motivo de o disco
de 30 GB sobrar com folga.

## 1.6 Infraestrutura atual (desenvolvimento)

`docker-compose.yml` com 4 serviços: `db` (volume `db_data`, healthcheck), `backend` (build
multi-stage gradle→temurin-jre-alpine), `ml-service` (python:3.10-slim), `frontend` (nginx:alpine
servindo bind mount). `.env` na raiz com credenciais do MySQL.

## 1.7 O que **não existe** hoje — e a nuvem cobra

| Lacuna | Impacto em produção |
|---|---|
| **Sem HTTPS / reverse proxy** | JWT trafegando em claro |
| **`JWT_SECRET` com default no `application.yml:37`** | Se a env var faltar, sobe com segredo público e versionado — qualquer um forja token |
| **Frontend com mock ligado por padrão** | O sistema publicado mostraria dados falsos |
| **Sem Spring Actuator** | Sem health check do backend para o Docker liberar/reiniciar o container |
| **`ml-service` sem autenticação** | Se ganhar porta pública, é motor de CPU aberto para qualquer um |
| **Motor síncrono e sequencial** (`MotorController.kt:33`) | Requisição de minutos (ver R1) |
| **Estado do job em memória** (decisão aprovada) | Backend não pode ter mais de 1 réplica |
| **`docker-compose.yml:55` monta `./frontend` inteiro** no nginx | Publicaria `CLAUDE.md`, `docs/`, `prototype/` e `design-reference/` |
| **Sem CI/CD** (não há `.github/`) | Deploy manual, sem gate de testes |
| **Sem backup automatizado** | Tratado em §7.2 |

---

# PARTE 2 — Requisitos que o código impõe à infraestrutura

Oito restrições que saem do código, não de preferência. São elas que justificam o desenho da Parte 3.

## 2.1 R1 — O lote do motor é longo e síncrono → **o timeout do proxy é o risco nº 1**

`MotorController.recalcular()` itera os produtos em sequência (`MotorController.kt:33`), e cada
iteração é um Feign `POST /predict` que treina Holt-Winters **e** Prophet. Com ~312 SKUs e a
estimativa documentada de 1–5 s/produto, o lote fica na casa de **5 a 25 minutos numa única
requisição HTTP**.

Na AWS, isso descartaria qualquer desenho com Application Load Balancer sem ajuste (padrão de 60 s)
e inviabilizaria completamente API Gateway (limite rígido de 29 s). **O desenho escolhido evita o
problema por construção:** o Caddy, como reverse proxy, **não impõe timeout de resposta por padrão**
— a requisição longa passa. É uma das razões de o proxy próprio ser preferível ao ALB aqui, além do
custo.

Isso **não resolve** o problema, apenas o adia: o navegador do lojista ainda fica minutos esperando.
A solução correta continua sendo o **Épico 7 (motor assíncrono, 202 + polling)**, já desenhado e
validado.

> **Pendência de dimensionamento:** `ml-service/benchmark_motor.py` (T-54) existe e está pronto, mas
> **nunca foi executado** — `docs/benchmark-motor.md` não existe no repositório. Rodar esse
> benchmark é o primeiro passo de qualquer dimensionamento de CPU, e o número medido entra na
> metodologia do TCC.

## 2.2 R2 — O ml-service é CPU-bound e hoje serializa tudo

Dois fatos somados:

1. O `Dockerfile` do ml-service sobe `uvicorn main:app` — **1 worker**.
2. `predict_router.py:15` declara `async def predict(...)`, mas o trabalho pesado dentro de
   `executar_previsao` é **síncrono** (`_tentar_holt_winters`/`_tentar_prophet` chamam código
   bloqueante direto). Numa corrotina, isso **trava o event loop**.

**Efeito colateral não óbvio:** enquanto um `/predict` roda, o `GET /health` **não responde**. Um
healthcheck do Docker com timeout curto marcaria o container como não-saudável **no meio do lote**.

**Mitigações** (ambas na Parte 8): trocar `async def predict` por `def predict` — o FastAPI passa a
executar no threadpool e o loop fica livre — e subir com `uvicorn --workers 2`, ganhando paralelismo
real nos 2 vCPU da instância.

## 2.3 R3 — Cold start do Prophet

A primeira previsão após subir o container paga a inicialização do modelo Stan e pode estourar o
`read-timeout` de 30 s do Feign (`application.yml`).

**Como o desenho trata:** na EC2 os containers são **processos permanentes** — o custo é pago uma
vez, na subida, e não a cada uso. É a vantagem concreta da VM sobre alternativas serverless com
scale-to-zero (Lambda, App Runner ocioso), que transformariam cada recálculo mensal numa execução
fria. A T-53 (warm-up no startup) continua desejável, mas deixa de ser bloqueante.

## 2.4 R4 — Imagem do ml-service é grande

`prophet` + `cmdstanpy` (com CmdStan empacotado) + `statsmodels` + `scikit-learn` + `pandas`/`numpy`
sobre `python:3.10-slim` resulta numa imagem de **ordem de 1,5–2,5 GB**. Na EC2 isso pesa no build
(ver §9.3) e no disco. O `.dockerignore` já exclui `venv/` e fixtures — **falta excluir `analysis/`
e `docs/`** (notebooks, 14 PNGs e PDFs sem função em runtime).

## 2.5 R5 — Estado em memória → backend fica em 1 réplica

A decisão validada em 2026-07-12 mantém o `MotorJobStatus` **em memória**. Consequência direta:
**não escalar o backend horizontalmente** — duas réplicas dariam status divergente conforme a que
atendesse o polling. Pelo mesmo motivo, o `@Scheduled` mensal (T-35) só é seguro com 1 réplica.

Para a carga real (1 mercado, 1–3 usuários), 1 réplica é sobra — e a instância única do desenho
satisfaz a restrição naturalmente. **Registrar como limitação conhecida**, não como defeito.

## 2.6 R6 — O ml-service não pode ter porta pública

`POST /predict` não tem autenticação alguma. Além de violar a invariante A1 do `CLAUDE.md`, um
endpoint público que treina dois modelos por requisição é um vetor de exaustão de CPU trivial.

**Requisito de rede:** o ml-service só pode ser alcançável de dentro. No desenho, ele vive na rede
interna do Docker **sem porta publicada** — o security group da EC2 sequer precisa saber que ele
existe.

## 2.7 R7 — Importação carrega o `.xlsx` em memória

Apache POI (`XSSFWorkbook`) materializa a planilha inteira na heap. Com o limite de 5 MB do
`application.yml:5`, o pico é da ordem de **10× o arquivo** — ~50 MB por importação. Define um piso
de heap: **container do backend com ≥ 1 GB**.

## 2.8 R8 — Segredos e configuração

`application.yml:37` tem `${JWT_SECRET:stocksense-dev-secret-...}`. O default versionado é
conveniente em dev e perigoso em produção: uma env var ausente não quebra o boot — o sistema sobe
com um segredo público. **Em produção o segredo deve ser obrigatório.** Mesma regra para
`DB_PASSWORD` e para a credencial seedada na `V2`.

---

# PARTE 3 — A arquitetura AWS

## 3.1 Onde cada componente roda

**Tudo roda numa única instância EC2**, como containers Docker. A AWS entra com a máquina, a rede,
o disco e o bucket de backup — não com um serviço gerenciado por componente.

| Componente | Onde roda | Porta | Acessível da internet? |
|---|---|---|---|
| **Caddy** (TLS + reverse proxy) | container na EC2 | **443 e 80 publicadas** | ✅ **sim — único ponto de entrada** |
| `frontend/web` | container nginx na EC2 | 80 interna | via Caddy, na rota `/` |
| `backend` (Spring Boot) | container na EC2 | 8080 interna | via Caddy, na rota `/api/*` |
| `ml-service` (FastAPI) | container na EC2 | 8000 interna | ❌ **não** — só o backend alcança |
| **MySQL 8.0** | container na EC2 | 3306 interna | ❌ **não** |
| Dados do MySQL | volume Docker sobre **EBS gp3 30 GB** | — | ❌ não |
| Backups | **S3** (`mysqldump` diário via cron) | — | ❌ não (IAM instance profile) |
| Logs | arquivos JSON do Docker na própria EC2, com rotação | — | ❌ não |

A leitura de uma linha só: **o único processo com porta aberta para a internet é o Caddy.** Todo o
resto conversa por dentro da rede Docker, onde os containers se enxergam pelo nome do serviço
(`backend`, `ml-service`, `db`) e a internet não enxerga nada.

## 3.2 Diagrama — camada 1: infraestrutura AWS

```
                              Internet
                                  │
                                  │  HTTPS 443  ·  HTTP 80 (redirect + ACME)
   ┌──────────────────────────────┼───────────────────────────────────────┐
   │  Conta AWS · Região us-east-1                                        │
   │                              │                                       │
   │                   ┌──────────▼───────────┐                           │
   │                   │  Internet Gateway    │                           │
   │                   └──────────┬───────────┘                           │
   │  VPC  10.0.0.0/16            │                                       │
   │  ┌───────────────────────────┼────────────────────────────────────┐  │
   │  │ Subnet PÚBLICA 10.0.1.0/24        (sem NAT Gateway — ver §4.2) │  │
   │  │                           │                                    │  │
   │  │   ┌───────────────────────▼───────────────────────────┐        │  │
   │  │   │ SG-web    entrada:  443/tcp  ← 0.0.0.0/0          │        │  │
   │  │   │                     80/tcp   ← 0.0.0.0/0          │        │  │
   │  │   │                     22/tcp   ← só o IP do dev     │        │  │
   │  │   │  ┌─────────────────────────────────────────────┐  │        │  │
   │  │   │  │  EC2  t3.medium · 2 vCPU / 4 GB             │  │        │  │
   │  │   │  │  Ubuntu 24.04 LTS · Elastic IP              │  │        │  │
   │  │   │  │                                             │  │        │  │
   │  │   │  │  ►►► os containers estão na camada 2 ◄◄◄    │  │        │  │
   │  │   │  └──────────────────┬──────────────────────────┘  │        │  │
   │  │   └──────────────────────┼─────────────────────────────┘        │  │
   │  │                          │  volume Docker db_data               │  │
   │  │                 ┌────────▼──────────┐                           │  │
   │  │                 │  EBS gp3 · 30 GB  │  ← dados do MySQL         │  │
   │  │                 └───────────────────┘     persistem ao desligar │  │
   │  └────────────────────────────────────────────────────────────────┘  │
   │                              │                                       │
   │                              │ IAM instance profile (s3:PutObject)   │
   │                     ┌────────▼───────────────┐                       │
   │                     │ S3 · stocksense-backup │  ← mysqldump diário   │
   │                     └────────────────────────┘                       │
   └──────────────────────────────────────────────────────────────────────┘
```

## 3.3 Diagrama — camada 2: containers dentro da EC2

```
   EC2 t3.medium ─── docker compose ─── rede interna "stocksense-net"
   ┌────────────────────────────────────────────────────────────────────┐
   │                                                                    │
   │  :443  ┌──────────────────────────────────────────────┐            │
   │ ──────►│  caddy      ← ÚNICO com porta publicada      │            │
   │  :80   │  TLS automático (Let's Encrypt)              │            │
   │        └───┬──────────────────────────────┬───────────┘            │
   │            │  rota  /                     │  rota  /api/*          │
   │   ┌────────▼─────────────┐     ┌──────────▼──────────────────┐     │
   │   │ frontend  (nginx)    │     │ backend  (Spring Boot)      │     │
   │   │ :80   interno        │     │ :8080  interno              │     │
   │   │ serve ./frontend/web │     └────┬───────────────────┬────┘     │
   │   └──────────────────────┘          │ Feign HTTP        │ JDBC     │
   │                          ┌──────────▼────────┐  ┌───────▼────────┐ │
   │                          │ ml-service        │  │ db (mysql 8.0) │ │
   │                          │ :8000  interno    │  │ :3306 interno  │ │
   │                          │ SEM porta pública │  │ volume db_data │ │
   │                          └───────────────────┘  └────────────────┘ │
   └────────────────────────────────────────────────────────────────────┘
```

## 3.4 Como uma requisição atravessa o sistema

Exemplo concreto: o lojista abre o dashboard.

1. O navegador resolve `stocksense.duckdns.org` → **Elastic IP** da EC2.
2. O pacote chega na VPC pelo **Internet Gateway** e é avaliado pelo **SG-web**: porta 443 está
   liberada para `0.0.0.0/0`, então passa. (Se tentasse a 8000 do ml-service, seria descartado aqui —
   a regra não existe.)
3. O **Caddy** termina o TLS e olha a rota. `/dashboard.html` não casa com `/api/*`, então vai para
   o container `frontend`, que devolve o HTML e os módulos JS.
4. O JS executa `apiGet('/dashboard')` — com `API_BASE_URL = '/api'`, a chamada sai para a **mesma
   origem**. Nada de CORS.
5. O Caddy recebe `/api/dashboard`, casa com a rota da API e repassa para `backend:8080` pela rede
   Docker.
6. O `JwtAuthFilter` valida o token, o `DashboardService` consulta `db:3306` e devolve o JSON.
7. Se a rota fosse `/api/motor/recalcular`, o backend abriria uma conexão Feign para
   `ml-service:8000` — **de dentro da rede Docker**, um caminho que não existe a partir da internet.

O ponto de projeto: **front e API na mesma origem**. Isso resolve, de uma vez, CORS (que o
`SecurityConfig` não configura hoje), certificado único e o isolamento do ml-service.

---

# PARTE 4 — Recursos AWS em detalhe

## 4.1 Inventário

| Recurso | Configuração | Papel |
|---|---|---|
| **VPC** | `10.0.0.0/16` | rede isolada do projeto |
| **Subnet pública** | `10.0.1.0/24`, uma AZ | onde a EC2 vive |
| **Internet Gateway** | anexado à VPC | entrada/saída de internet |
| **Route table** | `0.0.0.0/0` → IGW | rota padrão da subnet |
| **Security Group `SG-web`** | entrada 443 e 80 de `0.0.0.0/0`; 22 apenas do IP do desenvolvedor; saída liberada | firewall da instância |
| **EC2** | `t3.medium`, Ubuntu 24.04 LTS, key pair | roda todos os containers |
| **EBS** | `gp3`, 30 GB, root volume | SO, imagens Docker e dados do MySQL |
| **Elastic IP** | 1 endereço | IP fixo para o DNS |
| **S3** | bucket `stocksense-backup`, lifecycle de 30 dias | destino dos dumps |
| **IAM** | role + instance profile com `s3:PutObject` restrito ao bucket | a EC2 grava no S3 **sem access key no disco** |

**Região:** `us-east-1` — a mais barata. `sa-east-1` (São Paulo) reduz latência mas custa ~30–40% a
mais; irrelevante para uma demonstração, e o crédito é a restrição dominante.

## 4.2 Duas armadilhas de custo a evitar

**NAT Gateway — não deve existir neste desenho.** Custa ~US$ 32/mês *mais* tráfego, e sozinho
consumiria um terço do crédito por mês. Ele só é necessário quando recursos em subnet **privada**
precisam de saída para a internet. Como a EC2 está em subnet **pública** com IP próprio, ela sai
direto pelo Internet Gateway. Se alguma receita de arquitetura AWS sugerir "coloque a aplicação em
subnet privada", saiba que o preço dessa recomendação é um NAT Gateway.

**IPv4 público é cobrado desde 2024** — ~US$ 0,005/h (~US$ 3,6/mês) por endereço, inclusive Elastic
IP associado a instância **parada**. É o custo que continua correndo quando você desliga a VM para
economizar. Liberar o Elastic IP zera essa cobrança, ao preço de o IP mudar na próxima subida
(exigindo atualizar o DNS).

---

# PARTE 5 — Domínio e TLS

Let's Encrypt **não emite certificado para endereço IP** — é preciso um nome. Três caminhos:

| Opção | Custo | Observação |
|---|---|---|
| **DuckDNS** (`stocksense.duckdns.org`) | **grátis** | **Recomendado para a demonstração.** Aponta para o Elastic IP em 1 minuto; o Caddy emite o certificado sozinho na primeira subida |
| Domínio próprio (`.com`) | ~US$ 12/ano | Melhor apresentação na defesa; registrável em qualquer registrador, sem precisar de Route 53 |
| Route 53 hosted zone | +US$ 0,50/mês | Só se quiser o DNS dentro da AWS; não traz benefício técnico aqui |

O Caddy resolve TLS sozinho: aponta-se o nome no `Caddyfile` e ele obtém e renova o certificado via
ACME, usando a porta 80 (por isso ela está aberta no SG, além do redirect para HTTPS).

---

# PARTE 6 — Dimensionamento

## 6.1 Orçamento de memória — 4 GB da t3.medium

| Processo | Limite sugerido | Observação |
|---|---|---|
| `ml-service` | **1,8 GB** | Prophet + pandas + statsmodels; é o maior consumidor (R4) |
| `backend` | **1,0 GB** (`-XX:MaxRAMPercentage=70`) | JVM + POI carregando `.xlsx` (R7) |
| `db` (MySQL) | **0,6 GB** (`innodb_buffer_pool_size=256M`) | o dataset inteiro cabe em memória (§1.5) |
| `caddy` + `frontend` | **0,15 GB** | proxy e arquivos estáticos |
| Sistema operacional | ~0,35 GB | Ubuntu 24.04 mínimo |
| **Total** | **~3,9 GB** de 4 GB | |

Fica **apertado por projeto**, e o momento de pico é justamente o lote do motor, quando ml-service e
backend trabalham juntos. Mitigação obrigatória: **swapfile de 2 GB no EBS**, como rede de proteção
contra o OOM killer. Swap é lento, mas é preferível a perder o lote no meio de uma demonstração.

## 6.2 CPU

2 vCPU, com o `ml-service` rodando `uvicorn --workers 2` (R2) para usar os dois de fato. A t3 é
**burstable**: acumula créditos de CPU quando ociosa e os gasta em picos. Como o perfil de uso é
exatamente esse — ociosa quase sempre, pico durante o lote —, o modelo burstable favorece este
sistema. Vale monitorar `CPUCreditBalance` no CloudWatch durante o primeiro lote completo: se zerar,
a instância é limitada (*throttled*) e o lote se arrasta.

> **Antes de fechar esses números:** rodar `python benchmark_motor.py --produtos 50 150 300` com o
> ml-service no ar. É a diferença entre dimensionar por estimativa e por medição — e o resultado vai
> para a metodologia do TCC.

---

# PARTE 7 — Custo e consumo do crédito

## 7.1 Dois cenários

Preços de referência de `us-east-1`, on-demand:

| Item | Ligada 24/7 | Ligada sob demanda (~40 h/mês) |
|---|---|---|
| EC2 t3.medium (US$ 0,0416/h) | US$ 30,37 | US$ 1,66 |
| EBS gp3 30 GB | US$ 2,40 | US$ 2,40 |
| IPv4 público / Elastic IP | US$ 3,65 | US$ 3,65 |
| S3 (dumps) + transferência | < US$ 0,20 | < US$ 0,20 |
| **Total mensal** | **~US$ 36,60** | **~US$ 7,90** |
| **Duração de US$ 100** | **~2,7 meses** | **~12 meses** |

**Recomendação:** manter a instância desligada por padrão e ligá-la para trabalhar e demonstrar. O
crédito cobre o TCC inteiro com folga.

## 7.2 O que acontece ao desligar a instância

| Recurso | Ao parar a EC2 |
|---|---|
| Dados do MySQL (volume no EBS) | ✅ **persistem intactos** |
| Imagens Docker construídas | ✅ persistem |
| Containers | param; sobem de novo com `docker compose up -d` (ou `restart: unless-stopped`) |
| Cobrança de CPU/RAM | ✅ **para** |
| Cobrança de EBS e IPv4 | ❌ continua (~US$ 6/mês) |

Desligar não perde dado. E, mesmo no pior caso — instância terminada por engano, volume perdido —,
a recuperação é curta: **todo o dataset entra por `.xlsx` via `POST /api/importacao`**, e tudo o
mais no banco (`previsao`, `metrica_modelo`, `ponto_reposicao`, `classe_abc`) é **derivado**, obtido
rodando `POST /api/motor/recalcular`. Reimportar as duas planilhas e rodar o motor devolve o sistema
ao mesmo estado.

É exatamente esse raciocínio que justifica **não** contratar RDS: o backup gerenciado protege contra
uma perda que, aqui, custa minutos. O `mysqldump` diário para o S3 existe para poupar esses minutos,
não para evitar uma catástrofe.

## 7.3 Sobre o RDS, para registro no TCC

**RDS *é* MySQL 8.0** — não é outro banco. A ADR #1 do `CLAUDE.md` (MySQL 8.0 como SGBD único)
vale igual nos dois casos. Migrar custa **uma variável de ambiente**:

```
# hoje — container na VM
DB_URL=jdbc:mysql://db:3306/stocksense?useSSL=false&serverTimezone=UTC

# RDS
DB_URL=jdbc:mysql://stocksense.xxxx.us-east-1.rds.amazonaws.com:3306/stocksense?useSSL=true&serverTimezone=UTC
```

Mesmo driver, mesmas migrations Flyway, mesmas entidades JPA, zero linha de Kotlin alterada. Fica
documentado como **evolução para trabalhos futuros**, caso o parceiro adote o sistema em produção
real — aí o backup gerenciado, o patch automático e o *point-in-time restore* passam a valer o custo.

---

# PARTE 8 — Mudanças no código antes do deploy

Checklist executável. Todas as referências foram reconferidas contra o código em 2026-08-17.

| # | Arquivo | Mudança | Motivo |
|---|---|---|---|
| 1 | `frontend/web/js/core/config.js:1` | `API_BASE_URL = '/api'` | mesma origem via Caddy; elimina o `localhost:8080` e a necessidade de CORS |
| 2 | `frontend/web/js/core/apiClient.js:8` | inverter o default do mock | hoje o mock está **ligado** salvo opt-out no `localStorage` — publicaria dados falsos |
| 3 | `backend/src/main/resources/application.yml:37` | remover o default de `jwt.secret` e falhar o boot sem a env var | R8 |
| 4 | `backend/build.gradle.kts` | adicionar `spring-boot-starter-actuator`, expondo só `/actuator/health` | healthcheck do Docker |
| 5 | `ml-service/app/routers/predict_router.py:15` | `async def predict` → `def predict` | R2 — libera o event loop; o `/health` volta a responder durante o lote |
| 6 | `ml-service/Dockerfile:7` | acrescentar `--workers 2` ao `uvicorn` | R2 — usa os 2 vCPU |
| 7 | `ml-service/.dockerignore` | acrescentar `analysis/` e `docs/` | R4 — tira notebooks, 14 PNGs e PDFs da imagem |
| 8 | `backend/src/main/resources/db/migration/V2__seed_dados_padrao.sql:18` | trocar a credencial seedada (`admin@stocksense.local`) | o hash está versionado no repositório |

O item 8 merece cuidado: a `V2` já rodou nos bancos existentes, e o Flyway não reexecuta migration
aplicada. A troca deve entrar como **`V4`** nova (ou por `UPDATE` manual no banco de produção),
nunca editando a `V2` — a regra do `CLAUDE.md` §10 vale para todas as migrations já aplicadas, não
só para a `V1`.

---

# PARTE 9 — Runbook de deploy

## 9.1 Provisionamento AWS (console ou CLI)

1. Criar a **VPC** `10.0.0.0/16` com uma **subnet pública** `10.0.1.0/24`, **Internet Gateway** e
   rota `0.0.0.0/0` → IGW. *(A VPC default da conta também serve e poupa esta etapa; a VPC dedicada
   rende um diagrama melhor no capítulo de infraestrutura.)*
2. Criar o **security group `SG-web`**: entrada 443 e 80 de `0.0.0.0/0`; 22 apenas do seu IP.
3. Lançar a **EC2 t3.medium**, Ubuntu 24.04 LTS, 30 GB gp3, com o key pair e o `SG-web`.
4. Alocar e associar um **Elastic IP**.
5. Criar o **bucket S3** `stocksense-backup` e uma **IAM role** com `s3:PutObject` restrito a ele;
   anexar a role à instância como **instance profile**.
6. Cadastrar o subdomínio no **DuckDNS** apontando para o Elastic IP.

## 9.2 Preparo da instância

```bash
ssh -i chave.pem ubuntu@<elastic-ip>

# Docker + plugin compose
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker ubuntu && newgrp docker

# Swapfile de 2 GB — rede de proteção do §6.1
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

git clone <repo> stocksense && cd stocksense
```

## 9.3 Build — o ponto que costuma falhar

O build do backend roda Gradle + compilador Kotlin dentro do Docker e pede ~2 GB sozinho; o do
ml-service instala ~2 GB de dependências científicas. Numa máquina de 4 GB, **construir as duas
imagens em paralelo estoura a memória**. Construir uma de cada vez, com o swap já ativo:

```bash
docker compose -f docker-compose.prod.yml build ml-service
docker compose -f docker-compose.prod.yml build backend
```

Se ainda assim falhar, a alternativa é construir na máquina local e publicar as imagens (Docker Hub
ou ECR), deixando a EC2 apenas com `docker compose pull`.

## 9.4 `docker-compose.prod.yml`

Derivado do compose atual, com as correções desta análise:

```yaml
services:
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]          # únicas portas publicadas
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
    depends_on: [frontend, backend]

  frontend:
    image: nginx:alpine
    restart: unless-stopped
    volumes:
      - ./frontend/web:/usr/share/nginx/html:ro   # ./frontend/web — NÃO ./frontend
    # sem 'ports' — só o Caddy alcança

  backend:
    build: { context: ./backend }
    restart: unless-stopped
    environment:
      DB_URL: jdbc:mysql://db:3306/stocksense?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true
      DB_USERNAME: ${DB_USERNAME}
      DB_PASSWORD: ${DB_PASSWORD}
      ML_SERVICE_URL: http://ml-service:8000
      JWT_SECRET: ${JWT_SECRET}                   # obrigatório — sem default
      JAVA_TOOL_OPTIONS: "-XX:MaxRAMPercentage=70"
    depends_on:
      db: { condition: service_healthy }
    deploy: { resources: { limits: { memory: 1g } } }
    # sem 'ports'

  ml-service:
    build: { context: ./ml-service }
    restart: unless-stopped
    deploy: { resources: { limits: { memory: 1800m } } }
    # sem 'ports' — R6

  db:
    image: mysql:8.0
    restart: unless-stopped
    command: --innodb-buffer-pool-size=256M
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: stocksense
      MYSQL_USER: ${DB_USERNAME}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes: [db_data:/var/lib/mysql]
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10
    deploy: { resources: { limits: { memory: 600m } } }
    # sem 'ports' — o 3307 do compose de dev NÃO é publicado aqui

volumes:
  db_data:
  caddy_data:
```

Acrescentar rotação de log em todos os serviços
(`logging: { driver: json-file, options: { max-size: 10m, max-file: "3" } }`) — sem isso o EBS enche
sozinho ao longo dos meses.

## 9.5 `Caddyfile`

```
stocksense.duckdns.org {
    encode gzip

    handle /api/* {
        reverse_proxy backend:8080
    }

    handle {
        reverse_proxy frontend:80
    }
}
```

O Caddy redireciona 80 → 443 automaticamente e **não impõe timeout de resposta por padrão**, o que
deixa o lote longo do motor passar enquanto o Épico 7 não entra (R1).

## 9.6 Subida e validação

```bash
# .env de produção na VM (nunca versionado)
cat > .env <<'EOF'
DB_ROOT_PASSWORD=<senha forte>
DB_USERNAME=appuser
DB_PASSWORD=<senha forte>
JWT_SECRET=<32+ bytes aleatórios>
EOF
chmod 600 .env

docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps        # todos 'running'/'healthy'
docker compose -f docker-compose.prod.yml exec backend wget -qO- localhost:8080/actuator/health
docker compose -f docker-compose.prod.yml exec ml-service wget -qO- localhost:8000/health
```

Depois, pelo navegador: abrir `https://stocksense.duckdns.org`, fazer login, importar
`2_produtos.xlsx` e `5_vendas.xlsx`, disparar `POST /api/motor/recalcular` e conferir que dashboard,
alertas, curva ABC e comparativo de modelos exibem dados reais — não os do mock.

## 9.7 Backup

```bash
# /etc/cron.daily/stocksense-backup
docker compose -f /home/ubuntu/stocksense/docker-compose.prod.yml exec -T db \
  mysqldump -u root -p"$DB_ROOT_PASSWORD" stocksense | gzip > /tmp/dump.sql.gz
aws s3 cp /tmp/dump.sql.gz s3://stocksense-backup/$(date +%F).sql.gz
```

A instance profile IAM autentica a chamada — **nenhuma access key no disco**. Antes da defesa,
tirar também um **snapshot do EBS**: restaura a máquina inteira, não só o banco.

## 9.8 Ligar e desligar para economizar

```bash
aws ec2 stop-instances  --instance-ids i-xxxx    # para a cobrança de CPU/RAM
aws ec2 start-instances --instance-ids i-xxxx    # containers sobem por 'restart: unless-stopped'
```

Com o Elastic IP associado, o endereço não muda e o DNS continua válido.

---

# PARTE 10 — Riscos, limitações e pendências

## 10.1 Riscos priorizados

| Sev. | Risco | Mitigação |
|---|---|---|
| 🔴 | **Frontend publicado ainda em mock** — a demonstração mostraria dados falsos | Item 2 da Parte 8, antes de qualquer deploy |
| 🔴 | **`JWT_SECRET` default sobe em produção** | Item 3 da Parte 8 |
| 🔴 | **Lote do motor demora minutos** e o lojista fica esperando | Caddy sem timeout evita o corte da conexão; a experiência só melhora com o Épico 7 |
| 🟡 | **OOM na t3.medium** durante o lote (§6.1) | swapfile de 2 GB + limites de memória por container |
| 🟡 | **Build estourando memória** na própria instância (§9.3) | construir uma imagem por vez, ou construir local e dar `pull` |
| 🟡 | **Créditos de CPU burstable zerando** no lote completo | monitorar `CPUCreditBalance` no primeiro lote real |
| 🟡 | **nginx publicando o repositório inteiro** | montar `./frontend/web` (§9.4) |
| 🟢 | Crédito AWS acabando antes da defesa | manter a instância desligada por padrão (§7.1) |
| 🟢 | Crescimento de `previsao` por append | irrelevante nos volumes atuais |

## 10.2 Limitações conscientes — material de defesa

Não são defeitos; são escolhas com justificativa, e é assim que devem ser apresentadas à banca:

| Limitação | Justificativa |
|---|---|
| **Instância única, sem alta disponibilidade** | 1 estabelecimento, 1–3 usuários, uso não crítico. HA custaria mais que o crédito total |
| **Banco em container, não gerenciado** | Dados reconstruíveis por importação (§7.2); migração para RDS é uma variável de ambiente (§7.3) |
| **Backend limitado a 1 réplica** | Consequência do estado do job em memória (R5), decisão validada em 2026-07-12 |
| **Sem CI/CD** | Deploy manual é aceitável para uma demonstração; automatizar é evolução natural |
| **Motor síncrono** | Épico 7 desenhado e validado, suspenso aguardando o volume real de SKUs |

## 10.3 Pendências que travam decisões

1. **T-54 (benchmark do motor)** — script pronto, nunca executado. **Destravável hoje**, sem depender
   de ninguém, e é o insumo direto do dimensionamento de CPU (§6.2).
2. **Volume real de SKUs** — pendente do parceiro. Trava o Épico 7.
3. **Integração do frontend** — enquanto o front estiver em mock, o deploy entrega backend e ML sem
   produto navegável.

## 10.4 Ordem sugerida

| Fase | O quê | Depende de |
|---|---|---|
| 0 | Rodar o benchmark (T-54) e fechar o dimensionamento | nada — **fazer primeiro** |
| 1 | Aplicar os 8 itens da Parte 8 | nada |
| 2 | Criar `docker-compose.prod.yml` e `Caddyfile` | fase 1 |
| 3 | Provisionar a AWS e subir (Parte 9) | fase 2 |
| 4 | Cron de backup + snapshot antes da defesa | fase 3 |
| 5 | Épico 7 (motor assíncrono) | volume de SKUs / benchmark |

---

*Documento gerado a partir da auditoria do código em `code/` (2026-08-16, referências reconferidas
em 2026-08-17). Atualizar quando o benchmark for executado, o Épico 7 sair de suspenso ou a
infraestrutura for efetivamente provisionada.*
