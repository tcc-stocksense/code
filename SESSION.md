# SESSION.md — StockSense

## Cabeçalho do Projeto

| Campo | Valor |
|---|---|
| **Nome** | StockSense — Motor de Otimização Preditiva de Estoque |
| **Tipo** | TCC — Sistemas de Informação (2026) |
| **Repositório** | Monorepo: `backend/`, `ml-service/`, `frontend/` |
| **Stack** | Kotlin/Spring Boot · Python/FastAPI · MySQL 8 · HTML/CSS/JS |
| **Branch principal** | `main` |
| **Branches abertas** | `chore/infra-terraform-aws` (deploy/infra, **atual**, sincronizada com o origin); `feat/produto-detalhe-metricas` (Épico 4, pushed, sem PR); `feat/dashboard-alertas` (Épico 5, empilhada na anterior); `test/importacao-services` (T-17 testes + doc, pushed, sem PR); `analise-validacao-modelos` (T10 + pin do cmdstanpy, pushed, **sem merge na main**) |

> **Já mergeadas na `main`:** `feat/auth-login-jwt` (Épico 1, PR #4), `feat/motor-abc`
> (Épico 3, PR #5), `feat/t26-produto-listagem-edicao-estoque` (T-26, PR #6). A `main`
> contém Épicos 0–3 + T-26 + o Épico 4 desta sessão (após commit).
>
> **Ainda sem merge:** `test/importacao-services` (Épico 2 — testes T-17 + fix de doc dos
> 2 endpoints de importação). Independente, base `main` limpa; pode ir a qualquer momento.
> Enquanto não mergeada, os testes de importação **não estão na `main`**.

---

## Última Sessão — 2026-09-05 (Infra — versionamento do D1 parcial)

> Branch: `chore/infra-terraform-aws`. Sessão de auditoria do backlog de deploy e commit do
> que estava parado no working tree desde 2026-08-30. Nenhum código novo.

### O que foi desenvolvido

A sessão levantou **o que já estava feito mas não versionado** e fechou isso em dois commits.
As duas tasks abaixo estavam prontas no working tree desde a sessão de 2026-08-30, que nunca
foi registrada neste arquivo.

- **D-10 — `JWT_SECRET` obrigatório.** `application.yml` passa a ter `secret: ${JWT_SECRET}`
  sem default: variável ausente quebra o boot em vez de subir com o segredo versionado. O
  `docker-compose.yml` de desenvolvimento passou a injetar o **mesmo valor de antes**, agora
  explicitamente, via `${JWT_SECRET:-...}` — em dev nada muda.
- **D-12 — Spring Actuator.** Quatro arquivos: `build.gradle.kts` (dependência),
  `application.yml` (`management.endpoints.web.exposure.include: health` +
  `show-details: never`), `SecurityConfig.kt` (`/actuator/health` em `permitAll`) e
  `docker-compose.prod.yml` (healthcheck do backend descomentado).
  O `SecurityConfig` era o ponto que o backlog não previa: com `anyRequest().authenticated()`,
  o healthcheck do Docker tomaria 401 para sempre e o container ficaria `unhealthy` desde a
  subida.
- **D-46 — pin `cmdstanpy==1.2.4` na branch de deploy.** Uma linha em
  `ml-service/requirements.txt`, abaixo do `prophet==1.1.6`, idêntica à da
  `analise-validacao-modelos`. Sem ela o `pip install` do Dockerfile resolve o cmdstanpy livre
  (provavelmente 1.3.0), que quebra o backend Stan do Prophet 1.1.6 **em silêncio** — fallback
  para Holt-Winters, HTTP 200, e a comparação de modelos da T10 inválida sem erro visível.
  Destrava D-04, D-30 e D-33. Confirmado que o venv local tem o 1.2.4 instalado: o pin descreve
  o ambiente onde o benchmark do D-41 rodou.

### Decisões técnicas tomadas nesta sessão

- **`SESSION.md` continua único, na raiz.** Avaliada a criação de um `infra/SESSION.md`
  espelhando o split dos `tasks.md`. Descartado: `tasks.md` é backlog (tem dono e trilha,
  divide bem por área), `SESSION.md` é cronologia — e a sessão atravessa áreas (esta mexeu em
  4 arquivos de `backend/` para fechar duas tasks de `infra/`). Duas linhas do tempo criariam
  ambiguidade sobre qual é a atual, que é o que a seção "Como Retomar Esta Sessão" existe
  para evitar.
- **D-16 descartada** (trocar a credencial seedada da `V2` por uma `V4`). Migration é o
  instrumento errado — roda igual em todos os ambientes, só moveria o segredo de arquivo e
  quebraria o `admin123` que o `tasks-integracao.md` usa em dev. Virou **limitação
  consciente**, registrada no §10.2 do `infraestrutura-nuvem.md`.

### Estado do versionamento (levantado nesta sessão)

- **Já no remoto** (`f54aaf2`, em `origin/chore/infra-terraform-aws`): D-13 (async de fachada
  do `/predict`), D-15 (`.dockerignore` do ml-service) e D-41 (benchmark do motor →
  `docs/benchmark-motor.md`).
- **Commitado nesta sessão:** D-10, D-12, D-46 e a nota da D-16.
- **Commits locais não pushados, em outras branches** (decisão do usuário: não subir agora):
  `feat/importacao-produtos-vendas` → `03e1baf` (fixtures CSV de importação) e
  `feat/ml-service-motor-preditivo` → `066bab8` (gerador de CSV de produtos sintéticos).
- **Pushada mas nunca mergeada:** `analise-validacao-modelos`, 5 commits à frente da `main` —
  carrega o notebook e os PDFs da T10. O pin `cmdstanpy` dela foi copiado para esta branch na
  D-46, então o merge deixou de ser bloqueador de deploy — virou decisão sobre material do TCC.

### Pendências que ficaram em aberto

- ⚠️ **Efeito colateral do D-10, avisar no grupo:** quem roda o backend **fora do Docker**
  (IDE, `bootRun`) agora precisa exportar `JWT_SECRET`. O valor de dev só é reposto pelo
  `docker-compose.yml`.
- ⚠️ **D-46 fechada, mas não validada por build.** O pin está na branch; nenhum `docker build`
  do ml-service rodou com ele no lugar. Quem confirma que a imagem sobe com o Prophet de fato
  funcionando é o **D-04**.
- **Épico D0 inteiro** (D-03 → D-08) roda na máquina local, sem AWS e sem gastar crédito. O
  D-07 destrava o D-14, hoje marcado `aguardando medicao`.
- **Três decisões travando os Épicos D3/D4:** D-17 (como o código chega na EC2 —
  `BLOQUEADOR`), D-18 (domínio) e D-19 (deployar com o front em mock ou esperar a trilha B).
- **Trilha B em 0 de 11** (`frontend/docs/tasks-integracao.md`) — o app é 100% mock.
- **`backend/tasks.md` desatualizado:** a T-54 (benchmark) continua `[ ]` lá, embora o D-41 do
  `infra/tasks.md` registre a execução em 2026-08-30.

### Nota sobre este arquivo

A entrada anterior era de **2026-07-12**: a sessão de infra de **2026-08-30** (D-10, D-12,
D-13, D-15 e o benchmark) nunca foi registrada aqui, e o que se sabe dela está nas notas do
`infra/tasks.md`. Corrigidos também dois cabeçalhos órfãos — sobras de entradas antigas
prependidas por cima do título "Última Sessão" anterior.

---

## Sessão — 2026-07-10 (Épico 5 — Dashboard + Alertas + Curva ABC)

> Branch: `feat/dashboard-alertas`, **empilhada** sobre a `feat/produto-detalhe-metricas`
> (decisão do usuário — o Épico 4 ainda não foi mergeado). O PR do Épico 5 só fica limpo
> depois que o do 4 entrar na `main`.

### O que foi desenvolvido

Fechado o **Épico 5** — T-31 a T-34. Entrega `GET /api/alertas` (T5),
`GET /api/dashboard` (T2) e `GET /api/curva-abc` (T7).

- **Migration `V3__add_dias_ate_ruptura.sql` + persistência no Motor:** `dias_ate_ruptura`
  não era coluna de `produto` (o ml-service devolvia e o backend descartava). Decisão:
  **persistir** (não derivar em memória) — alertas e dashboard precisam do valor em lote
  (ordenação + COUNT). `MotorService` agora grava `produto.diasAteRuptura`.
- **T-31 Alertas:** `AlertaService`/`Controller` + `AlertaResponse`. Semáforo relativo ao
  ponto de reposição (VERMELHO ≤ PR; AMARELO ≤ PR×1.5; VERDE acima), ordenado por urgência.
  Produtos sem PR (motor nunca rodou) ficam fora. `leadTimeMedio` expõe
  `MotorService.LEAD_TIME_PADRAO` (3, tornado público — fonte única).
- **T-32 Dashboard:** `DashboardService`/`Controller` + `DashboardResponse`. Contagens por
  queries derivadas na nova coluna; `mapeMedioSelecionado` via JPQL considerando só a
  execução mais recente por produto; série de faturamento agregada por dia no SQL e por
  semana (segunda-feira) no Kotlin. **Só histórico** (~8 semanas) — projeção e "valor em
  risco" ficaram fora por decisão.
- **T-33 Curva ABC:** método de leitura `curvaAbc` no `AbcService` + `AbcController`.
  Resposta `CurvaAbcResponse(abcProxy, itens)` — wrapper deliberado para expor a limitação
  do proxy, conforme CLAUDE.md §6.
- **T-34 Testes:** `AlertaServiceTest` (7), `DashboardServiceTest` (6), +4 de curva no
  `AbcServiceTest`, +1 assert no `MotorServiceTest`. Suíte completa: **40 testes, 0 falhas**
  (JDK 21 temporário, revertido para 17).

### Decisões técnicas tomadas nesta sessão

| Decisão | Motivo |
|---|---|
| Persistir `dias_ate_ruptura` (migration V3) em vez de derivar da `previsao` em memória | Dashboard faz COUNT e alertas ordenam por urgência — em lote, derivar exigiria N consultas ou query complexa; o ml-service já devolve o valor |
| `leadTimeMedio` no alerta = default 3 do Motor | `ProdutoFornecedor` não existe; exibir o mesmo valor que o motor usou no PR é honesto; campo passa a refletir o real quando a entidade existir |
| Série de faturamento só histórico (sem 4 semanas projetadas) | Texto da T-32; projeção exigiria previsao × preço por produto — fica para a integração do frontend |
| Agregação diária no SQL + semana no Kotlin | Testável em unidade; independe de função de data do MySQL |
| `mapeMedioSelecionado` só da execução mais recente por produto | O motor grava em append; média sobre o histórico todo distorceria o KPI |
| Branch empilhada sobre a do Épico 4 | Decisão do usuário; PRs devem ser mergeados em ordem (4 → 5) |

### Pendências que ficaram em aberto

- **PRs em ordem:** mergear `feat/produto-detalhe-metricas` (Épico 4) e depois
  `feat/dashboard-alertas` (Épico 5).
- Restam no backend: **T-35** (`MotorScheduler`, MVP-opcional) e Pós-MVP (T-36 a T-38).
- `test/importacao-services` continua sem merge.
| Decisão | Motivo |
|---|---|
| `demandaMediaDiaria` e `diasAteRuptura` derivados da tabela `previsao` (média dos 30 pontos mais recentes), **não** do histórico de vendas como o texto da T-27 dizia | A premissa do `mapeamento` exige "demanda **prevista**"; a tabela `previsao` já tem os pontos → sem migration, sem tocar no ml-service. Nenhum dos dois valores é persistido em `produto` |
| `ProdutoDetalheResponse` completo (σ + CV + tendência 14×14), não só os KPIs de reposição | O `mapeamento` (fonte de verdade das telas) pede variabilidade e tendência na T6; σ vem de `produto.desvioPadraoDemanda` (resolvido antes), CV e tendência são baratos |
| `MetricaService` separado, não embutido no `ProdutoService` | Padrão "um service por responsabilidade" do CLAUDE.md; a T10 é um domínio próprio (comparativo de modelos) |
| Detalhe e métricas com checagem de tenant (estabelecimento do JWT) | Consistência com `atualizarEstoque` (T-26); evita leitura cross-tenant |

### Verificação

Build e suíte validados com toolchain temporário **JDK 21** (o ambiente só tem JDK 21 e
não há rede para o Gradle provisionar o 17 — mesma situação das sessões anteriores);
`./gradlew test` → **BUILD SUCCESSFUL, 23 testes, 0 falhas**. Toolchain **revertido para
17** antes de qualquer commit (sem diff no `build.gradle.kts`).

### Pendências que ficaram em aberto

- Épico 4 **não commitado** ainda (aguardando o usuário).
- **Épico 5 (Dashboard/Alertas)** é o próximo — T-31 a T-34 (ver "Próxima Sessão").
- `test/importacao-services` (T-17 testes + fix de doc dos 2 endpoints) continua **sem
  merge** na `main` — os testes de importação não estão na `main`.

---

## Sessão — 2026-07-12 (Planejamento — Motor Assíncrono)

> **Sessão de análise e documentação — nenhum código implementado.** Saída: um épico novo de
> tarefas + um relatório técnico validado pelo orientador. Nada commitado; todas as mudanças estão
> no working tree (arquivos de docs/tasks).

### O que foi feito

**1. Diagnóstico do motor preditivo (síncrono → assíncrono).** Análise do desenho atual: o motor
roda **100% síncrono e sequencial** — `MotorController.recalcular()` faz um `for` sobre todos os
produtos, cada um com chamada Feign bloqueante ao ml-service. Único gatilho real hoje é o endpoint
manual (`@Scheduled` mensal e disparo pós-importação estão só nos docs, sem código). Risco central:
com ~312 SKUs o lote leva **minutos** numa única requisição HTTP e estoura o timeout do
navegador/proxy (o read-timeout Feign de 30 s protege só cada produto, não o agregado).

**2. Decisões de arquitetura registradas** (D1–D5 no relatório): núcleo único + duas cascas;
editar estoque de 1 produto **não** re-roda o motor (só `dias_ate_ruptura`/semáforo, calculados na
leitura); o contrato assíncrono (202 + status) é superconjunto e vira o padrão do front; **o
polling é responsabilidade do frontend** (backend só expõe `GET /api/motor/status`); não há
"endpoint de resultado" novo.

**3. Tarefas criadas:**
- `backend/tasks.md` → **Épico 7 — Motor Assíncrono** (T-39–T-46 backend, T-47–T-51 frontend).
- `frontend/tasks.md` → **FASE 1.5 — Motor assíncrono** (F9 núcleo `motorStatus.js` + polling;
  S3+ ajuste da Importar; S6+ recálculo por produto).

**4. Relatório técnico:** `docs/relatorio-motor-assincrono.md` (também publicado como Artifact para
enviar ao orientador).

**5. Validação do orientador (com ressalvas) — decisões aplicadas hoje:**
- Volume de SKUs: **ainda não confirmado** → Épico 7 marcado **SUSPENSO** (não iniciar
  implementação) até o parceiro confirmar.
- Estado do job em memória (T-40): **aprovado**; limitação documentada (*perde em restart; lote
  idempotente, re-disparável manualmente*).
- Contrato de `GET /api/motor/status` (T-42): **aprovado e congelado**.
- Lote síncrono de debug (T-45): **descartado** (T-43, síncrono de 1 produto, permanece).
- **3 lacunas** viraram tarefas novas no Épico 7: **T-52** (guard de concorrência 409 nos três
  gatilhos), **T-53** (warm-up do Prophet no startup do ml-service), **T-54** (benchmark do lote —
  **prioridade imediata**, roda antes da confirmação de SKUs e alimenta a metodologia). **T-55**
  trata a omissão do `is_promocional`, **reclassificada como risco ALTO para a validade acadêmica**
  da comparação Holt-Winters × Prophet (corrigir o `montarRequest` **ou** documentar na metodologia).

**6. Esboço do benchmark (T-54).** Criado `ml-service/benchmark_motor.py` — mede **N chamadas
`/predict` sequenciais** (o custo dominante do lote; a orquestração Spring/DB é desprezível perto
do Prophet), nos volumes **50/150/300**, reusando `generate_synthetic_data.py`. Faz **warm-up** do
Prophet, conta chamadas que estouram os 30 s do Feign e grava a tabela em `docs/benchmark-motor.md`
(para a metodologia). Envia `is_promocional` vazio de propósito (reproduz o backend atual). O
caminho ponta a ponta via `POST /api/motor/recalcular` ficou como stub (`medir_e2e()`).
⚠️ **Só a sintaxe foi validada** (`py -m py_compile` OK); **não executado** — depende do ml-service
no ar e do **Prophet ativo** (CmdStan quebrado localmente, ver "Pendente e Bugs Conhecidos"). Com o
Prophet caído, o script mede só Holt-Winters e **avisa** que os números não são confiáveis. Nota
registrada na T-54 do `backend/tasks.md`.

### Decisões técnicas tomadas nesta sessão

| Decisão | Motivo |
|---|---|
| Recálculo em lote vira **assíncrono** (202 + polling), síncrono só para 1 produto | Lote de ~312 SKUs estoura o timeout da requisição; 1 produto (~1–5 s) cabe nos 30 s do Feign |
| Estado do job **em memória** (`MotorJobStatus`), sem tabela | Escopo TCC single-instance; lote idempotente cobre a perda em restart |
| **Guard de concorrência único** (T-52) para os 3 gatilhos | Evita recálculos simultâneos; disparo pós-importação é único, no "Processar dados" |
| Épico 7 **suspenso** até confirmar volume de SKUs, exceto benchmark | Decidir prioridade (MVP × MVP-opcional) com número medido, não estimativa |
| `is_promocional`: reclassificado ALTO (validade acadêmica), não baixo | Regressor exógeno é vantagem potencial do Prophet sendo desligada — enviesa a Tela 10 |

### Pendências que ficaram em aberto

- **Volume real de SKUs** — pendente do parceiro; destrava o Épico 7.
- **T-54 (benchmark)** — script **esboçado** (`ml-service/benchmark_motor.py`), falta **executar**;
  bloqueado pelo CmdStan/Prophet quebrado localmente. É a única tarefa do épico liberada para rodar já.
- **T-55 (`is_promocional`)** — decisão metodológica (corrigir × documentar) a alinhar com o orientador.
- Mudanças desta sessão são **só documentação, não commitadas** — avaliar em que branch entram.

---

## Sessão — 2026-07-10 (Épico 4 — Produto: detalhe + métricas)

> Branch: `feat/produto-detalhe-metricas` (criada a partir da `main`). Commitada
> (`ca09c15`) e pushed; PR ainda não aberto.

### O que foi desenvolvido

Fechado o **Épico 4 (Produto)** — T-27 a T-30. Completa os 4 endpoints de
`/api/produtos/*` e entrega as telas T6 (detalhe) e T10 (comparativo de modelos).

- **T-27 — Detalhe do produto** (`GET /api/produtos/{id}/detalhe`): `ProdutoService.detalhe`
  + `ProdutoDetalheResponse`. DTO completo conforme o mapeamento T6 — demanda média,
  variabilidade (σ + CV), tendência (média dos primeiros 14 × últimos 14 dias com venda),
  KPIs de reposição e série de previsão mais recente.
- **T-28 — Comparativo de modelos** (`GET /api/produtos/{id}/metricas`): `MetricaService`
  próprio + `MetricaResponse`. Retorna as 2 métricas mais recentes (uma por modelo),
  vencedor primeiro. Alimenta a Tela 10.
- **T-29 — Controller:** os dois endpoints novos ligados ao `ProdutoController` que já
  existia da T-26; ambos com checagem de tenant (produto de outro estabelecimento → 404).
- **T-30 — Testes:** `ProdutoServiceTest` de 4 → 9 testes; `MetricaServiceTest` novo (4).
  Suíte completa: **23 testes, 0 falhas**.

**Arquivos:** 4 novos (`ProdutoDetalheResponse`, `MetricaResponse`, `MetricaService`,
`MetricaServiceTest`) + 5 modificados (`PrevisaoRepository`, `MetricaModeloRepository`,
`ProdutoService`, `ProdutoController`, `ProdutoServiceTest`) + `backend/tasks.md`
(T-27→T-30 marcadas).

### Decisões técnicas tomadas nesta sessão

| Decisão | Motivo |
|---|---|
| `demandaMediaDiaria` e `diasAteRuptura` derivados da tabela `previsao` (média dos 30 pontos mais recentes), **não** do histórico de vendas como o texto da T-27 dizia | A premissa do `mapeamento` exige "demanda **prevista**"; a tabela `previsao` já tem os pontos → sem migration, sem tocar no ml-service. Nenhum dos dois valores é persistido em `produto` |
| `ProdutoDetalheResponse` completo (σ + CV + tendência 14×14), não só os KPIs de reposição | O `mapeamento` (fonte de verdade das telas) pede variabilidade e tendência na T6; σ vem de `produto.desvioPadraoDemanda` (resolvido antes), CV e tendência são baratos |
| `MetricaService` separado, não embutido no `ProdutoService` | Padrão "um service por responsabilidade" do CLAUDE.md; a T10 é um domínio próprio (comparativo de modelos) |
| Detalhe e métricas com checagem de tenant (estabelecimento do JWT) | Consistência com `atualizarEstoque` (T-26); evita leitura cross-tenant |

### Verificação

Build e suíte validados com toolchain temporário **JDK 21** (o ambiente só tem JDK 21 e
não há rede para o Gradle provisionar o 17 — mesma situação das sessões anteriores);
`./gradlew test` → **BUILD SUCCESSFUL, 23 testes, 0 falhas**. Toolchain **revertido para
17** antes de qualquer commit (sem diff no `build.gradle.kts`).

### Pendências que ficaram em aberto

- Épico 4 **não commitado** ainda (aguardando o usuário).
- **Épico 5 (Dashboard/Alertas)** é o próximo — T-31 a T-34 (ver "Próxima Sessão").
- `test/importacao-services` (T-17 testes + fix de doc dos 2 endpoints) continua **sem
  merge** na `main` — os testes de importação não estão na `main`.

---

## Sessão — 2026-07-10 (ml-service: remoção do ABC + T-05)

### O que foi desenvolvido

#### ml-service (Python/FastAPI)

- **Revisão completa do `ml-service/tasks.md`** contra o código real: o arquivo dizia
  que só existiam `__init__.py` vazios, mas quase todo o MVP já estava implementado.
  Tabela "Estado atual" e as 19 tasks corrigidas para refletir a realidade —
  **15/19 concluídas**.
- **Dívida técnica da ADR #3 resolvida:** `app/services/abc_service.py` e
  `app/tests/test_abc_service.py` foram **removidos** — o ml-service ainda calculava e
  devolvia `classe_abc`/`abc_proxy` no `PredictResponse`, contrariando a decisão de que
  ABC vive só no backend (`AbcService`). `prediction_service.py` não chama mais
  `classificar_abc`.
- **T-05 (cross-service) resolvido:** `desvio_padrao_demanda` adicionado ao
  `PredictResponse` do ml-service — `prediction_service.py` agora expõe o `σ` da série
  (já calculado internamente para a fórmula de Ballou). Verificado ponta a ponta:
  `executar_previsao()` chamado com série sintética, valor retornado bate exatamente
  com `serie.std()`.
- Suíte de testes do ml-service ajustada (`test_predict_router.py`) para o novo schema.
  53/53 testes relevantes passando (Prophet excluído — 11 falhas por
  `AttributeError: 'Prophet' object has no attribute 'stan_backend'`, problema de
  instalação do CmdStan neste venv, não bug de código).

#### backend (Kotlin/Spring Boot)

- **T-05 fechado do lado do backend também:** `PredictResponse.kt` (Feign DTO) ganhou o
  campo `desvioPadraoDemanda: BigDecimal?`; `MotorService.executarMotor()` agora grava
  `produto.desvioPadraoDemanda = resp.desvioPadraoDemanda` a cada execução;
  `MotorServiceTest` atualizado para cobrir a persistência.
  `@JsonIgnoreProperties(ignoreUnknown = true)` mantido por tolerância a campos futuros
  — `classe_abc`/`abc_proxy` nunca existiram neste DTO.
- Suíte completa (`./gradlew test`) validada com toolchain temporário JDK 21 (mesma
  situação da sessão 2026-07-08: só há JDK 21 no ambiente, sem rede para o Gradle
  provisionar o 17) — **build successful**, toolchain revertido para 17 antes de
  qualquer commit.

#### Documentação atualizada em conjunto

`ml-service/CLAUDE.md`, `ml-service/tasks.md`, `backend/CLAUDE.md` (§4), `backend/tasks.md`
(T-05, T-19, T-21, T-27), `docs/mapeamento-funcionalidades.md` (T6),
`docs/revisao-arquitetura.md` (ADR #3, tabela de contrato, checklist de dívidas
técnicas) — todos os lugares que citavam a pendência de `desvio_padrao_demanda` ou a
divergência do ABC no ml-service foram atualizados para refletir a resolução.

### Pendências que ficaram em aberto

- **T-03 (ml-service)** — `.env.example` ainda não existe.
- **T-10 (ml-service)** — regressor `is_promocional` do Prophet não implementado
  (`MVP-opcional`, não bloqueia).
- **Ambiente Prophet quebrado localmente** — CmdStan precisa ser reinstalado no venv do
  ml-service (ver seção "Pendente e Bugs Conhecidos" abaixo).
- **`backend/REVIEW.md`** — arquivo staged no git (`A backend/REVIEW.md`) espelhando o
  `CLAUDE.md` antigo do backend, aparentemente um artefato de revisão do usuário. Não foi
  tocado nesta sessão.

---

## Sessão — 2026-07-08

### O que foi desenvolvido

#### backend (Kotlin/Spring Boot) — branch `claude/branch-status-gcfufm`

- **Reorganização de branch:** a `claude/branch-status-gcfufm` foi recriada a partir da
  `feat/motor-abc` (que já contém Épico 1 — Auth e Épico 3 — Motor + ABC, ainda sem PR),
  e os 5 commits de docs que só existiam na `main` (tutorial local, SESSION.md de auth/
  motor, guia de revisão de arquitetura) foram trazidos por cima via cherry-pick, sem
  conflitos. Motivo: a `main` sozinha não tem `estabelecimentoId` em `Produto` nem
  `RecursoNaoEncontradoException` — pré-requisitos reais da T-26.
- **T-26 — `ProdutoService` (listagem e edição de estoque):** implementada.
  `ProdutoController` (`GET /api/produtos`, `PATCH /api/produtos/{id}/estoque`) foi
  criado junto, antecipando parte da T-29. `atualizarEstoque` valida que o produto
  pertence ao estabelecimento do JWT antes de editar.
- **`ProdutoServiceTest`** — 4 testes (MockK), cobrindo a fatia de T-26 dentro da T-30
  (listagem ordenada por nome, edição de estoque persiste só o campo, produto
  inexistente e produto de outro estabelecimento → `RecursoNaoEncontradoException`).
  Os cenários de detalhe do produto (T-27) continuam bloqueados por T-05.
- ⚠️ **JDK 17 ausente no ambiente:** só há JDK 21 instalado, sem rede para o Gradle
  provisionar o toolchain (mirror de segurança do Ubuntu 404, sem `foojay-resolver`).
  Contornado apontando o toolchain para 21 **apenas localmente** (mudança revertida
  logo depois, nunca commitada) só para rodar `./gradlew test`: suíte completa passou,
  14 testes / 0 falhas. Recomendo rodar de novo com JDK 17 real antes do PR.

---

## Sessão — 2026-07-04

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
  **[Resolvido em 2026-07-10 — ver sessão no topo.]**
- O ml-service **não devolve `desvio_padrao_demanda`** (calcula e descarta) — confirma a
  pendência **T-05**. Fora do contrato Feign por ora; bloqueia só a T-30 (Épico 4).
  **[Resolvido em 2026-07-10 — ver sessão no topo.]**
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
  **[T-05 resolvido em 2026-07-10 — ver sessão no topo.]**
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
| PR de `feat/auth-login-jwt` (Épico 1) | ✅ Mergeada | PR #4 na `main` |
| PR de `feat/motor-abc` (Épico 3) | ✅ Mergeada | PR #5 na `main` |
| PR de `feat/t26-produto-listagem-edicao-estoque` (T-26) | ✅ Mergeada | PR #6 na `main` |
| Épico 4 (Produto — T-27 a T-30) | ⚠️ Feito, sem commit | Branch `feat/produto-detalhe-metricas`; 23 testes passando; falta commitar + PR |
| PR de `test/importacao-services` (Épico 2 testes/doc) | ⚠️ Pendente | Branch pushed, falta abrir e mergear — independente, base `main` limpa. **T-17 e o fix de doc dos 2 endpoints ainda não estão na `main`** |
| T-05 — acordo `desvio_padrao_demanda` no `PredictResponse` | ✅ Resolvido (2026-07-10) | ml-service devolve o campo; `MotorService` grava em `produto.desvioPadraoDemanda`; não bloqueia mais T-27 |
| ml-service ainda devolve `classe_abc`/`abc_proxy` | ✅ Resolvido (2026-07-10) | `abc_service.py` removido do ml-service; ABC só existe no `AbcService` do backend |
| T-17 — testes unitários de importação | ✅ Feito | 13 testes na `test/importacao-services`, todos passando |
| `estabelecimentoId` ausente na entidade `Produto` | ✅ Resolvido | Adicionado na `feat/motor-abc` (Épico 3) |
| CLAUDE.md do backend sobre `/api/importacao` | ✅ Corrigido na branch | Atualizado para 2 endpoints na `test/importacao-services`; chega na `main` no merge |
| Fornecedor / ProdutoFornecedor (MVP-opcional) | ❌ Não feito | Sem essas entidades, o lead time do Motor cai sempre no default (3 / 1.0) |

---

## Próxima Sessão — Fazer nesta ordem

> Atualizado em 2026-07-10 (após o Épico 5).

### Passo 1: Mergear os PRs em ordem

1. Abrir e mergear o PR da `feat/produto-detalhe-metricas` (Épico 4, commit `ca09c15`).
2. Depois abrir e mergear o PR da `feat/dashboard-alertas` (Épico 5 — empilhada na
   anterior; o diff só fica limpo após o merge do 4).
3. Mergear `test/importacao-services` (T-17 + fix de doc) — independente, pode ir a
   qualquer momento; enquanto não mergeada, os testes de importação não estão na `main`.

### Passo 2: Validar ponta a ponta com o banco real

- Subir MySQL + backend (`docker-compose up -d db && ./gradlew bootRun`) — a migration
  **V3** roda na subida. Importar planilhas, rodar `POST /api/motor/recalcular` e conferir
  `GET /api/alertas`, `GET /api/dashboard` e `GET /api/curva-abc` com dados reais.

### Passo 3: O que resta no backend

- **T-35** `MotorScheduler` (`@Scheduled` mensal) — MVP-opcional, pequeno.
- Avaliar `Fornecedor`/`ProdutoFornecedor` (lead time real no Motor, hoje default 3/1.0).
- Pós-MVP: T-36 a T-38.

### Depois: frontend

- Integração das telas com os endpoints já prontos (T1–T7 e T10 têm API completa).

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
