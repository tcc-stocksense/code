# Tasks — Backend (Kotlin / Spring Boot)

> Organização por **domínio**: cada épico entrega entidade + repo + DTOs + service + controller juntos.
> Sem dependências para frente entre épicos. A ordem dos épicos é a ordem natural de desenvolvimento.
>
> Legenda de prioridade: **MVP** · **MVP-opcional** · **Pós-MVP**
> Status: `[ ]` pendente · `[x]` concluído · `[-]` em progresso

---

## Estado atual (auditado em 2026-07-03)

- Migrations prontas: `V1__create_schema.sql` (schema completo) e `V2__seed_dados_padrao.sql` (seed)
- `application.yml` configurado (DB, Flyway, Feign timeouts, `ML_SERVICE_URL`)
- **Épico 2 (Importação) já tem núcleo funcional**

---

## Épico 0 — Fundação `MVP`

> Infraestrutura transversal. Pré-requisito inevitável para todos os outros épicos.
> Nenhuma regra de negócio aqui.

- [x] **T-01 — Estrutura de pacotes** `MVP`
  Criar os pacotes com `package` declarations:
  `controller`, `service`, `repository`, `domain`, `dto/request`, `dto/response`,
  `client`, `exception`, `config`
  Pacote raiz: `br.com.stocksense`

- [x] **T-02 — Dependências novas no `build.gradle.kts`** `MVP`
  Adicionar:
  - `io.jsonwebtoken:jjwt-api`, `jjwt-impl`, `jjwt-jackson` (0.12+) — JWT
  - `org.springframework.boot:spring-boot-starter-security` — Spring Security
  - `org.springframework.security:spring-security-test` (testes)
  - `org.apache.poi:poi-ooxml:5.3.0` — leitura de `.xlsx`
  _Depende de: T-01_
  Nota: `jjwt-*` fixado em `0.12.6`; `poi-ooxml` está em `5.2.5` (não `5.3.0`, sem impacto conhecido).

- [x] **T-03 — `SecurityConfig` temporário** `MVP` *(pulado deliberadamente)*
  Desabilitar CSRF e liberar todos os endpoints (`permitAll`).
  **Objetivo único:** não bloquear o desenvolvimento enquanto o JWT não está implementado.
  Será substituído integralmente na T-09 (Épico 1).
  _Depende de: T-02_
  Nota: como o Épico 1 foi feito de uma vez, fomos direto para o `SecurityConfig`
  definitivo (T-09) — não fazia sentido implementar uma versão temporária só para
  substituí-la minutos depois.

- [x] **T-04 — Exceptions de domínio + `GlobalExceptionHandler`** `MVP`
  Exceptions: `MotorPreditivoException`, `ImportacaoException(erros: List<String>)`,
  `RecursoNaoEncontradoException`.
  `GlobalExceptionHandler` (`@RestControllerAdvice`) com handlers:
  - `MethodArgumentNotValidException` → 400 + lista de campos
  - `RecursoNaoEncontradoException` → 404
  - `MotorPreditivoException` → 502
  - `ImportacaoException` → 400 + lista de erros
  - `Exception` (fallback) → 500 sem stack trace no body
  Todas as respostas em `ProblemDetail` (RFC 7807).
  _Depende de: T-01_
  Nota: `ImportacaoException` no código é `(message: String)`, não `(erros: List<String>)`
  — a lista de erros por linha vai no DTO de resposta (`ErroLinha`), não na exception.
  `EntityNotFoundException` (jakarta) também tem handler próprio, mantido por compatibilidade.

- [x] **T-05 — Acordo cross-service: `desvio_padrao_demanda` no ml-service** `MVP`
  ⚠️ **Não é código — é um alinhamento com o time.**
  O ml-service precisa adicionar `desvio_padrao_demanda: float` ao `PredictResponse`
  antes de implementar T-30 (detalhe do produto, Épico 4).
  Registrar a decisão e atualizar o CLAUDE.md do ml-service quando confirmado.
  _Não bloqueia os épicos 1–3, bloqueia T-30._
  **Resolvido em 2026-07-10:** ml-service passou a devolver `desvio_padrao_demanda` no
  `PredictResponse` (confirmado com teste ponta a ponta batendo com `serie.std()`). Backend
  atualizado em conjunto: `PredictResponse.kt` mapeia o campo, `MotorService.executarMotor()`
  grava em `produto.desvioPadraoDemanda`, `MotorServiceTest` cobre a persistência. T-27 já
  pode ser implementada sem essa dependência pendente.

---

## Épico 1 — Domínio Auth / T1 `MVP`

> Entrega: `POST /api/auth/login` funcionando com JWT.

- [x] **T-06 — Entidade `Estabelecimento` + `EstabelecimentoRepository`** `MVP`
  Entidade: `id` (auto), `nomeFantasia`, `cnpj`, `endereco`, `email` (unique), `senhaHash`.
  Repository: `JpaRepository<Estabelecimento, Int>` +
  `findByEmail(email: String): Estabelecimento?` (necessário para login).
  _Depende de: T-01_

- [x] **T-07 — `JwtConfig` + `JwtService`** `MVP`
  `JwtConfig`: bean com `jwt.secret` e `jwt.expiration-ms` via `application.yml` — nunca hardcodar.
  `JwtService`: `gerarToken(estabelecimentoId: Int): String`,
  `validarToken(token: String): Boolean`,
  `extrairEstabelecimentoId(token: String): Int`.
  Subject do token = `estabelecimentoId.toString()`.
  _Depende de: T-02_
  `JwtConfig` implementado como `@ConfigurationProperties(prefix = "jwt")`, registrado via
  `@EnableConfigurationProperties(JwtConfig::class)` em `StockSenseApplication`.

- [x] **T-08 — DTOs de auth + `AuthService`** `MVP`
  DTOs: `LoginRequest(email, senha)` com `@field:NotBlank`; `LoginResponse(token, estabelecimentoId, nomeFantasia)`.
  `AuthService.login(email, senha)`: busca por email, valida BCrypt, lança
  `RecursoNaoEncontradoException` para email não encontrado ou senha errada
  (mesma mensagem — não vazar qual falhou). Retorna `LoginResponse` com JWT.
  _Depende de: T-04, T-06, T-07_

- [x] **T-09 — `JwtAuthFilter` + `SecurityConfig` definitivo** `MVP`
  `JwtAuthFilter` (`OncePerRequestFilter`): extrai Bearer token, valida via `JwtService`,
  popula `SecurityContextHolder`.
  `SecurityConfig` definitivo: substitui T-03. Libera `POST /api/auth/login`;
  protege todo o resto (`authenticated()`). Adiciona `JwtAuthFilter` antes de
  `UsernamePasswordAuthenticationFilter`.
  _Depende de: T-07_
  ⚠️ Consequência: `/api/importacao/produtos` e `/api/importacao/vendas` (Épico 2) agora
  exigem `Authorization: Bearer <token>` — antes estavam completamente abertos.

- [x] **T-10 — `AuthController`** `MVP`
  `POST /api/auth/login` → chama `AuthService.login()`, retorna `LoginResponse`.
  _Depende de: T-04, T-08, T-09_

- [x] **T-11 — Testes unitários: `AuthService`** `MVP`
  Cenários: credenciais válidas, email não encontrado, senha incorreta.
  MockK em `EstabelecimentoRepository` e `BCryptPasswordEncoder`.
  _Depende de: T-08_
  `AuthServiceTest` com MockK — 3 testes, todos passando (`./gradlew test`).

---

## Épico 2 — Domínio Importação / T3 `MVP`

> Entrega: ingestão de `.xlsx` processando e persistindo no banco. Sem motor ainda.
> **Decisão do time:** implementado como **dois endpoints separados**
> (`POST /api/importacao/produtos` e `POST /api/importacao/vendas`), não um único
> `POST /api/importacao` multipart. Cada planilha tem seu service e sua resposta.

- [x] **T-12 — Entidades de importação + Repositories** `MVP` / `MVP-opcional`
  **MVP:** `Produto`, `Venda` (+ `ProdutoRepository`, `VendaRepository`) — feitos.
  **MVP-opcional:** `Fornecedor` / `ProdutoFornecedor` + repositories — **ainda não feitos**
  (o Motor usa lead time no default enquanto não existirem).
  _Depende de: T-06_

- [x] **T-13 — DTOs de importação** `MVP`
  `ProdutoImportacaoResponse(totalLinhas, importados, erros)`,
  `VendaImportacaoResponse(totalLinhas, importados, diasDeHistorico, erros, avisos)`,
  `ErroLinha(linha, mensagem)`.
  ⚠️ `ProdutoResponse`/`ProdutoEstoqueRequest` (consumo/edição de produto) pertencem ao Épico 4,
  ainda não criados.
  _Depende de: T-01_

- [x] **T-14 — Parsing e validação** `MVP`
  `ProdutoImportacaoService` e `VendaImportacaoService` com Apache POI. Erros por linha
  acumulados em `erros[]`; erros de estrutura lançam `ImportacaoException` → `400`.
  Histórico < 90 dias vira **aviso** (não erro). Planilhas desejáveis ainda sem endpoint.
  _Depende de: T-04, T-12, T-13_

- [x] **T-15 — Persistência** `MVP`
  Produtos: upsert por `produto_id`. Vendas: deduplicação por produto no período
  (`deleteByProdutoIdAndDataHoraBetween`) antes de inserir.
  _Depende de: T-14_

- [x] **T-16 — `ImportacaoController`** `MVP`
  `POST /api/importacao/produtos` e `POST /api/importacao/vendas` (multipart, campo `arquivo`).
  Zero lógica no controller.
  _Depende de: T-04, T-15_

- [x] **T-17 — Testes unitários de importação** `MVP`
  `ProdutoImportacaoServiceTest` (6) e `VendaImportacaoServiceTest` (7) — planilhas `.xlsx`
  reais em memória (POI + `MockMultipartFile`). Cenários: planilha válida, `produto_id`
  duplicado, coluna obrigatória ausente, `estoque_atual` negativo, campo calculado preenchido,
  arquivo não-`.xlsx`, produto inexistente, data inválida, `quantidade ≤ 0`, `valor_venda` com
  vírgula, histórico < 90 dias (aviso). Todos passando.
  _Depende de: T-15_
  ⚠️ Cenário "planilhas desejáveis ausentes (defaults)" do spec original não se aplica: os
  endpoints atuais só recebem produtos e vendas.

---

## Épico 3 — Domínio Motor + ABC `MVP`

> Entrega: `POST /api/motor/recalcular` chamando o ml-service, persistindo previsões,
> métricas e classificação ABC.

> **Implementado na branch `feat/motor-abc`** (base: `feat/auth-login-jwt`, pois o
> Épico 3 depende do Spring Security e da `RecursoNaoEncontradoException` do Épico 1).
> Todos os testes passando; queries JPQL validadas executando contra o MySQL real.

- [x] **T-18 — Entidades `Previsao` + `MetricaModelo` + Repositories** `MVP`
  `Previsao`: `id` auto, `produtoId`, `dataPrevisao: LocalDate`, `quantidadePrevista?`,
  `modeloUtilizado?`, `executadoEm: LocalDateTime`.
  `MetricaModelo`: `id` auto, `produtoId`, `modelo` (String), `mape?`, `rmse?`, `mae?`,
  `selecionado: Boolean`, `executadoEm`.
  Repositories: `PrevisaoRepository`, `MetricaModeloRepository`.
  _Depende de: T-12_
  Também adicionado `estabelecimentoId` à entidade `Produto` (a coluna já existia no `V1`),
  necessário para o filtro por estabelecimento no ABC e no controller.

- [x] **T-19 — DTOs do contrato Feign** `MVP`
  `VendaDiaria(data: LocalDate, quantidade: Int)`.
  `PredictRequest(produtoId, historico, leadTimeMedio, variabilidadeLeadTime, nivelServicoAlvo, estoqueAtual, isPromocional)`.
  `MetricasModelo(mape, rmse, mae)`.
  `PrevisaoDiaria(data, quantidadePrevista)`.
  `PredictResponse(produtoId, modeloSelecionado, previsoes, metricas, pontoReposicao,
  estoqueSeguranca, diasAteRuptura?, desvioPadraoDemanda?, aviso?)`.
  _Depende de: T-01_
  Mapeamento snake_case via `@JsonNaming` (sem mexer no ObjectMapper global).
  ✅ **Atualizado em 2026-07-10 (T-05):** `desvioPadraoDemanda` **agora está no contrato** —
  o ml-service passou a devolvê-lo. `@JsonIgnoreProperties(ignoreUnknown = true)` mantido por
  tolerância a campos futuros; `classe_abc`/`abc_proxy` (a antiga dívida técnica da ADR #3)
  foram removidos do response do ml-service e nunca existiram neste DTO.

- [x] **T-20 — `MlServiceClient`** `MVP`
  `@FeignClient(name = "ml-service", url = "\${ml.service.url}")`.
  Métodos: `predict(PredictRequest): PredictResponse`, `health(): Map<String, String>`.
  `@EnableFeignClients` já estava na classe principal (vem do Épico 1).
  _Depende de: T-19_

- [x] **T-21 — `MotorService`** `MVP`
  `montarRequest`: **agrega vendas por dia** (`agregarVendasDiarias`, SUM por data) — o
  ml-service espera série diária; lê `nivelServicoAlvo`/`estoqueAtual` de `Produto`.
  `@Transactional executarMotor(produtoId)`: chama Feign (→ `MotorPreditivoException` em falha),
  salva as previsões e as 2 métricas (flag `selecionado`), atualiza `produto` com
  `pontoReposicao`/`estoqueSeguranca`/`dataUltimoCalculo`.
  _Depende de: T-18, T-19, T-20_
  ⚠️ Lead time usa os **defaults** (3 / 1.0) — `ProdutoFornecedor` ainda não existe.
  ✅ **Atualizado em 2026-07-10 (T-05):** `executarMotor()` agora grava
  `produto.desvioPadraoDemanda = resp.desvioPadraoDemanda`. `MotorServiceTest` cobre a
  persistência (build validado localmente com toolchain temporário JDK 21 — revertido
  para 17 antes do commit).

- [x] **T-22 — `AbcService`** `MVP`
  `recalcularAbc(estabelecimentoId): AbcResultado`. Ranking por faturamento (SUM valor_venda),
  ordena DESC, % acumulada, atribui A (≤80%) / B (≤95%) / C — com o primeiro produto sempre A
  (corrige o caso de produto único). Fallback para `quantidade` como proxy quando qualquer
  produto está sem `valor_venda` (`abcProxy = true`). Atualiza `produto.classe_abc`.
  _Depende de: T-12_

- [x] **T-23 — `MotorController`** `MVP`
  `POST /api/motor/recalcular`: pega o estabelecimento do JWT, roda `executarMotor` por produto
  (cada um em sua transação, via proxy — falha isolada não aborta o lote), depois `recalcularAbc`.
  Resposta: `{ produtosProcessados, produtosComFalha, produtosClassificadosAbc, abcProxy, executadoEm }`.
  _Depende de: T-04, T-21, T-22_

- [x] **T-24 — Testes unitários: `MotorService`** `MVP`
  Sucesso (persiste previsões/métricas, atualiza produto), falha do ml-service →
  `MotorPreditivoException`, produto inexistente → `RecursoNaoEncontradoException`.
  _Depende de: T-21_

- [x] **T-25 — Testes unitários: `AbcService`** `MVP`
  Limites 80%/95%, produto único → A, fallback por quantidade, sem vendas → 0 classificados.
  _Depende de: T-22_

---

## Épico 4 — Domínio Produto / T4 + T6 + T10 `MVP`

> Entrega: todos os endpoints de `/api/produtos/*` funcionando.
> ⚠️ Épico 3 deve estar concluído — os campos calculados de `produto` só existem após o motor rodar.

- [x] **T-26 — `ProdutoService` — listagem e edição de estoque** `MVP`
  `listarTodos(estabelecimentoId: Int): List<ProdutoResponse>`
  `atualizarEstoque(produtoId: Int, estoqueAtual: Int): ProdutoResponse`
  Lançar `RecursoNaoEncontradoException` se produto não encontrado.
  _Depende de: T-04, T-12, T-13_
  `ProdutoController` criado junto (`GET /api/produtos`, `PATCH /api/produtos/{id}/estoque`)
  — antecipa parte da T-29, já que os dois endpoints não dependem de T-27/T-28.
  `atualizarEstoque` recebe também o `estabelecimentoId` do JWT e só atualiza o produto
  se ele pertencer ao estabelecimento autenticado (senão, `RecursoNaoEncontradoException`)
  — não estava explícito na task, mas evita edição cross-tenant agora que `Produto` tem
  `estabelecimentoId`.
  ⚠️ O ambiente de dev não tem JDK 17 instalado (só JDK 21) nem rede para o Gradle
  provisionar o toolchain (mirror de segurança do Ubuntu retornou 404; sem plugin
  `foojay-resolver`). Build e testes foram verificados apontando o toolchain para 21
  **apenas localmente** (mudança não commitada, revertida em seguida) — `test` passou
  100% (14 testes, 0 falhas). Rodar de novo com JDK 17 real antes de abrir PR, por garantia.

- [x] **T-27 — `ProdutoService` — detalhe do produto** `MVP`
  DTO: `ProdutoDetalheResponse` com KPIs calculados (`pontoReposicao`, `estoqueSeguranca`,
  `diasAteRuptura`, `desvioPadraoDemanda`), demanda média diária e série de previsão
  mais recente (últimas 30 linhas de `previsao` pelo maior `executadoEm`).
  `detalhe(produtoId: Int): ProdutoDetalheResponse`
  ✅ T-05 resolvido (2026-07-10) — `produto.desvioPadraoDemanda` já é populado pelo motor.
  **Implementado em 2026-07-10 (branch `feat/produto-detalhe-metricas`):**
  - **Decisão de fonte da demanda:** `demandaMediaDiaria` e `diasAteRuptura` são derivados
    da **previsão** (média dos 30 pontos de `previsao` mais recentes), não do histórico de
    vendas como dizia o texto original. Motivo: a premissa do `mapeamento` exige "demanda
    prevista", e a tabela `previsao` já tem esses pontos — sem migration, sem tocar no
    ml-service. `diasAteRuptura = estoqueAtual / demandaMedia` (null se demanda 0/ausente).
  - **DTO completo (mapeamento T6):** além dos KPIs, inclui `coeficienteVariacao`
    (σ/demandaMedia) e `tendenciaPercentual` (média dos primeiros 14 × últimos 14 dias com
    venda; null se < 28 dias). Query nova `PrevisaoRepository.findPrevisaoMaisRecente`;
    reuso de `VendaRepository.agregarVendasDiarias` para a tendência.
  - Checagem de tenant (produto de outro estabelecimento → `RecursoNaoEncontradoException`),
    igual ao `atualizarEstoque`. Degrada com graça quando o motor ainda não rodou.
  _Depende de: T-04, T-12, T-18, T-21_

- [x] **T-28 — `MetricaService` — comparativo de modelos** `MVP`
  DTO: `MetricaResponse(modelo, mape, rmse, mae, selecionado, executadoEm)`.
  `metricas(produtoId: Int): List<MetricaResponse>`: retorna as 2 linhas mais recentes
  de `metrica_modelo` para o produto (pelo maior `executadoEm`) — alimenta a Tela 10.
  Lançar `RecursoNaoEncontradoException` se produto não encontrado.
  _Depende de: T-04, T-18_
  **Implementado em 2026-07-10:** `MetricaService` próprio (não dentro do `ProdutoService`).
  Query `MetricaModeloRepository.findMetricasMaisRecentes`; vencedor (`selecionado`) primeiro
  na lista; checagem de tenant; lista vazia quando o motor ainda não rodou.

- [x] **T-29 — `ProdutoController`** `MVP`
  Todos os endpoints de produto em um único controller:
  - `GET /api/produtos` → `listarTodos()`
  - `PATCH /api/produtos/{id}/estoque` → `atualizarEstoque()` com `@Valid @RequestBody`
  - `GET /api/produtos/{id}/detalhe` → `detalhe()`
  - `GET /api/produtos/{id}/metricas` → `metricas()`
  _Depende de: T-04, T-26, T-27, T-28_
  **Implementado em 2026-07-10:** os dois endpoints novos ligados ao `ProdutoController` que
  já existia da T-26; `metricas` delega ao `MetricaService`.

- [x] **T-30 — Testes unitários: `ProdutoService`** `MVP`
  Cenários: listagem retorna lista correta, edição de estoque atualiza apenas o campo,
  produto não encontrado → exception, detalhe calcula demanda média corretamente.
  _Depende de: T-26, T-27_
  **Implementado em 2026-07-10:** `ProdutoServiceTest` estendido para 9 testes (detalhe:
  demanda/dias/CV/tendência corretos, sem previsão → nulos, < 28 dias → sem tendência,
  inexistente e cross-tenant → exception) + `MetricaServiceTest` novo (4 testes). Suíte
  completa: 23 testes, 0 falhas (build validado com toolchain temporário JDK 21, revertido
  para 17 antes do commit).

---

## Épico 5 — Domínio Dashboard + Alertas / T2 + T5 + T7 `MVP`

> Entrega: endpoints de consulta e visualização.
> ⚠️ Épicos 3 e 4 devem estar concluídos — dashboards consomem dados do motor e do ABC.

- [ ] **T-31 — `AlertaService` + `AlertaController`** `MVP`
  DTO: `AlertaResponse(produtoId, nome, estoqueAtual, pontoReposicao, diasAteRuptura,
  leadTimeMedio, semaforo: String)`.
  Semáforo calculado:
  - `"VERMELHO"` → `estoque_atual ≤ ponto_reposicao`
  - `"AMARELO"` → `ponto_reposicao < estoque_atual ≤ ponto_reposicao × 1.5`
  - `"VERDE"` → acima
  `GET /api/alertas`: lista ordenada por urgência (vermelhos primeiro).
  _Depende de: T-04, T-12, T-22_

- [ ] **T-32 — `DashboardService` + `DashboardController`** `MVP`
  DTO: `DashboardResponse(riscoDeFaltar7Dias, criticoAgora, mapeMedioModeloSelecionado,
  seriesFaturamento: List<{ semana, total }>)`.
  `GET /api/dashboard`:
  - `riscoDeFaltar7Dias`: `COUNT produtos WHERE dias_ate_ruptura ≤ 7`
  - `criticoAgora`: `COUNT WHERE dias_ate_ruptura < 3`
  - `mapeMedioModeloSelecionado`: média de `mape` das `metrica_modelo` com `selecionado = true`
    (não fixo no Prophet — usa o modelo vencedor de cada produto)
  - `seriesFaturamento`: `SUM(valor_venda)` agrupado por semana dos últimos 2 meses
  _Depende de: T-04, T-12, T-18, T-31_

- [ ] **T-33 — `AbcController`** `MVP`
  DTO: `AbcItemResponse(produtoId, nome, classeAbc, faturamento, percentualDoTotal, percentualAcumulado)`.
  `GET /api/curva-abc`: produtos com `classe_abc` preenchida, ordenados por faturamento DESC,
  com % do total e % acumulada calculadas na query ou no service.
  _Depende de: T-04, T-12, T-22_

- [ ] **T-34 — Testes unitários: `AlertaService`** `MVP`
  Cenários: semáforo vermelho (`estoque ≤ PR`), amarelo (`PR < estoque ≤ PR×1.5`), verde.
  _Depende de: T-31_

---

## Épico 6 — Agendamento `MVP-opcional`

- [ ] **T-35 — `MotorScheduler`** `MVP-opcional`
  Habilitar `@EnableScheduling` na classe principal.
  `@Scheduled(cron = "0 0 3 1 * *")` → roda todo dia 1 às 3h.
  Chama o **núcleo compartilhado** `processarLoteMotor()` (ver T-39) para cada
  estabelecimento — **passando pelo guard de concorrência da T-52** (não dispara se já houver
  job `PROCESSANDO`) —, que roda `executarMotor()` por produto e depois `recalcularAbc()`.
  Logar início, fim e quantidade processada.
  _Depende de: T-39, T-52_
  ⚠️ Antes do Épico 7 esta task chamaria `MotorService.executarMotor()` direto num loop.
  Após o Épico 7, deve reusar o núcleo `processarLoteMotor()` e o guard da T-52 — é um dos
  **três gatilhos** que compartilham o mesmo ponto de entrada (manual, pós-importação, cron).

---

## Épico 7 — Motor Assíncrono + Progresso `SUSPENSO`

> 🔒 **STATUS: SUSPENSO (validado pelo orientador com ressalvas em 2026-07-12).**
> **Não iniciar a implementação** das tarefas de async (T-39–T-44, T-46) até o **parceiro
> confirmar o volume real de SKUs** por estabelecimento — esse número decide se o épico é
> `MVP` ou `MVP-opcional`. **Exceção:** a **T-54 (benchmark)** tem prioridade **IMEDIATA** e
> **deve** rodar antes da confirmação — é ela que substitui a estimativa "10–20+ min" por um
> número medido e destrava a decisão de prioridade. As demais tarefas ficam desenhadas e
> prontas para começar assim que o volume for confirmado.
>
> **Motivação.** Hoje `POST /api/motor/recalcular` (T-23) processa **todos os produtos
> sequencialmente numa única requisição HTTP síncrona**: `for` sobre os produtos, cada
> um com uma chamada Feign bloqueante ao ml-service (Prophet é CPU-bound, ~1–5 s/produto).
> Com volume alto de SKUs (o Guia cita ~312, número **ainda não confirmado**), o lote leva
> **minutos** e estoura o timeout do navegador/proxy muito antes de terminar — mesmo com o
> read-timeout Feign de 30 s protegendo cada produto individualmente. Este épico remove esse
> risco tornando o lote assíncrono, sem perder a opção síncrona onde ela é barata.
>
> **Decisões de validação (orientador, 2026-07-12):**
> - **Volume de SKUs — pendente.** Épico SUSPENSO até confirmação do parceiro (ver status acima).
> - **Estado do job em memória (T-40) — APROVADO.** Limitação consciente documentada: *o estado
>   se perde em restart; o lote é idempotente e pode ser re-disparado manualmente*. Não justifica
>   tabela `execucao_motor` no escopo do TCC.
> - **Contrato de `GET /api/motor/status` (T-42) — APROVADO e CONGELADO** como proposto.
> - **Lote síncrono de debug (antiga T-45) — DESCARTADO.** Removido do épico. O caminho síncrono
>   que **permanece** é só o de **1 produto** (T-43).
> - **3 lacunas identificadas na revisão** viraram tarefas: **T-52** (guard de concorrência 409),
>   **T-53** (warm-up do Prophet), **T-54** (benchmark do lote). E **T-55** trata a omissão do
>   `is_promocional` (reclassificada como risco ALTO para a validade acadêmica da comparação).
>
> **Decisões de desenho (registradas em 2026-07-12):**
> - **Núcleo único, duas cascas.** O loop do lote vira um método `processarLoteMotor()`; os
>   endpoints síncrono/assíncrono e o scheduler (T-35) são invólucros finos em volta dele.
>   Adicionar/remover uma casca é reversível (~10 linhas) — a decisão **não** prende o projeto.
> - **Editar estoque de 1 produto NÃO re-roda o motor.** Previsão, ponto de reposição e
>   estoque de segurança dependem do *histórico de vendas*, não do `estoque_atual`. Só mudam
>   `dias_ate_ruptura` (`estoque ÷ demanda`) e o semáforo (relativo ao PR) — aritmética barata,
>   **calculada na leitura** pelos endpoints de tela (T-31/T-32), sem chamar o ml-service.
>   `PATCH /estoque` (T-26) continua sendo só um `UPDATE`. **Não criar recálculo no PATCH.**
> - **O contrato assíncrono (202 + status) é o que o front consome por padrão.** É um
>   **superconjunto**: com poucos SKUs o status volta "concluído" quase instantâneo (polling
>   para na 1ª tentativa); com muitos, aguenta. O caminho síncrono que sobra é só o de 1 produto.
> - **Quem faz o polling é o FRONTEND.** O backend só **expõe** `GET /api/motor/status`
>   (uma leitura). O loop que chama esse endpoint a cada ~3 s é responsabilidade do front.
> - **Não há "endpoint de resultado" novo.** O resultado do motor é o banco atualizado; ao
>   concluir, o front apenas re-busca os endpoints de tela já existentes (`/dashboard`,
>   `/produtos`, `/alertas`).

### Backend

- [ ] **T-39 — Extrair núcleo compartilhado `processarLoteMotor()`** `MVP`
  Refatorar a lógica de lote hoje embutida no `MotorController.recalcular()` (T-23) para um
  método reutilizável — em `MotorService` ou num novo `MotorLoteService`:
  `processarLoteMotor(estabelecimentoId: Int, onProgress: (feitos: Int, total: Int) -> Unit = {}): ResultadoLote`.
  Faz o loop por produto (cada `executarMotor` na sua transação, falha isolada não aborta o
  lote — comportamento atual preservado), depois `recalcularAbc()`, e chama `onProgress` a
  cada produto concluído. Retorna `{ produtosProcessados, produtosComFalha, produtosClassificadosAbc, abcProxy }`.
  **Sem mudança de comportamento** — só extração; `POST /recalcular` continua funcionando igual até T-41.
  _Depende de: T-21, T-22, T-23_

- [ ] **T-40 — Estado do job em memória (`MotorJobStatus`)** `MVP`
  Bean singleton que guarda o estado do recálculo por estabelecimento:
  `{ estado: PENDENTE|PROCESSANDO|CONCLUIDO|FALHOU, feitos: Int, total: Int, iniciadoEm, concluidoEm?, resumo?: ResultadoLote }`.
  *(o "executando" citado na revisão = estado `PROCESSANDO` do contrato congelado — ver T-42/T-52.)*
  Thread-safe (`AtomicReference`/`ConcurrentHashMap` por `estabelecimentoId`).
  ✅ **APROVADO na validação (2026-07-12)** como solução do escopo TCC. **Limitação consciente a
  documentar** (no `PredictResponse`/README e na metodologia): *o estado se perde em restart; o
  lote é idempotente e pode ser re-disparado manualmente*. Evolução futura (fora do escopo):
  tabela `execucao_motor`.
  _Depende de: T-39_

- [ ] **T-41 — `POST /api/motor/recalcular` assíncrono (202)** `MVP`
  Habilitar `@EnableAsync` na classe principal + configurar um `TaskExecutor` dedicado
  (pool pequeno, ex. 1–2 threads — o gargalo é o ml-service single-worker).
  O endpoint: valida estabelecimento (JWT), passa pelo **guard de concorrência da T-52**
  (`409 Conflict` se já houver job `PROCESSANDO`), marca `PROCESSANDO`, dispara
  `processarLoteMotor()` em background (atualizando `MotorJobStatus` via `onProgress`) e
  responde **`202 Accepted`** na hora, com `{ status: "processando", statusUrl: "/api/motor/status" }`.
  _Depende de: T-39, T-40, T-52_
  ⚠️ Substitui o comportamento síncrono da T-23 (que deixa de existir — o lote síncrono de debug
  foi **descartado**, ver T-45). O único caminho síncrono que resta é o de 1 produto (T-43).

- [ ] **T-42 — `GET /api/motor/status`** `MVP`
  Lê `MotorJobStatus` do estabelecimento autenticado e devolve o **contrato de status**:
  - processando → `{ estado: "PROCESSANDO", feitos, total }`
  - concluído → `{ estado: "CONCLUIDO", feitos, total, produtosComFalha, produtosClassificadosAbc, abcProxy, executadoEm }`
  - nunca rodou → `{ estado: "PENDENTE" }`
  Endpoint **leve e idempotente** — é o que o front vai chamar em loop (polling). Sem efeitos colaterais.
  ✅ **Contrato CONGELADO na validação (2026-07-12)** — aprovado como proposto. Não alterar o
  formato (nomes de estado, campos) sem novo acordo com o front, que passa a depender dele.
  _Depende de: T-40_

- [ ] **T-43 — `POST /api/motor/recalcular/{produtoId}` síncrono** `MVP-opcional`
  Recálculo de **um único produto** — rápido (~1–5 s), cabe nos 30 s do Feign, então
  **síncrono** é o paradigma certo aqui. Chama `motorService.executarMotor(produtoId)` (valida
  posse pelo estabelecimento do JWT) e devolve o resumo do produto. Uso: re-importou vendas de
  1 item, ou botão "recalcular este produto". **Não** recalcula ABC (ranking relativo — deixar
  para o lote), ou recalcula só se for barato — decidir na implementação.
  _Depende de: T-21_

- [ ] **T-44 — Disparar motor assíncrono ao fim da importação** `MVP`
  Dispara o lote assíncrono (reusa o caminho da T-41 — passa pelo guard da T-52, marca
  `PROCESSANDO`, `processarLoteMotor()` em background).
  ⚠️ **Disparo ÚNICO (validação 2026-07-12):** o recálculo acontece **uma só vez, no sucesso do
  "Processar dados"** (quando o gestor conclui a importação do conjunto obrigatório) — **nunca**
  por planilha individual (`/produtos` e `/vendas` são enviadas separadamente, mas o motor só roda
  ao final, uma vez). Se o guard indicar job em andamento, não dispara de novo (o lote pendente já
  cobre os dados novos).
  A resposta inclui `statusUrl` para o front acompanhar via polling. Importar produtos sem vendas
  novas **não** dispara o motor.
  _Depende de: T-41, T-52, T-16_

- [x] **T-45 — ~~Lote síncrono como ferramenta de debug~~ — DESCARTADO** `—`
  ❌ **Descartado na validação (2026-07-12).** Decisão do orientador: não expor um endpoint de
  lote síncrono (`/recalcular-sync`) — evita um caminho paralelo que o front poderia usar por
  engano e que reintroduziria o risco de timeout. O único caminho síncrono que **permanece** é o
  de **1 produto** (T-43). O corpo síncrono do lote da T-23 é substituído de vez pelo assíncrono (T-41).

- [ ] **T-46 — Testes: núcleo, async e status** `MVP`
  `processarLoteMotor()`: progresso reportado, falha isolada não aborta o lote, ABC ao final.
  `MotorJobStatus`: transições de estado, rejeição de job concorrente (409).
  `/api/motor/status`: os três estados (pendente/processando/concluído).
  Recálculo por produto (T-43): sucesso e produto de outro estabelecimento → 404.
  _Depende de: T-39, T-40, T-41, T-42, T-43_

### Frontend

> Estas tasks vivem no repositório do front (`frontend/`), registradas aqui só para manter o
> plano do fluxo assíncrono completo num lugar. **O "polling" é inteiramente frontend** — o
> backend só expõe `GET /api/motor/status` (T-42).

- [ ] **T-47 — Disparo + estado "processando" (consumir o 202)** `MVP`
  Ao acionar "Recalcular" ou concluir uma importação: tratar a resposta **`202`**, guardar o
  `statusUrl` e entrar em estado visual "processando" (spinner/banner, botão desabilitado para
  não disparar em duplicidade). Tratar `409 Conflict` (já há recálculo rodando) mostrando
  "recálculo em andamento".
  _Depende de: T-41, T-44_

- [ ] **T-48 — Polling de `GET /api/motor/status`** `MVP`
  Loop no front: chamar `/api/motor/status` a cada ~3 s enquanto `estado == "PROCESSANDO"`,
  atualizando o progresso (`feitos/total`) quando disponível. Parar o loop ao receber
  `CONCLUIDO` ou `FALHOU`. Incluir teto de tentativas/tempo para não pollar infinito se o
  backend cair. **Substitui o "dar reload manual"** — evita o usuário ver estado pela metade.
  _Depende de: T-42, T-47_

- [ ] **T-49 — Recarregar as telas ao concluir** `MVP`
  Quando o polling receber `CONCLUIDO`: parar o spinner, mostrar resumo (ex.: "312 processados,
  2 falhas") e **re-buscar os endpoints de tela** já existentes (`/api/dashboard`,
  `/api/produtos`, `/api/alertas`, `/api/curva-abc`) para refletir os dados novos. Não existe
  "endpoint de resultado" do motor — o resultado é o banco, lido por essas telas.
  _Depende de: T-48, T-32, T-33_

- [ ] **T-50 — Recálculo por produto (síncrono) na tela de detalhe** `MVP-opcional`
  Botão "recalcular este produto" na Tela 6, chamando `POST /api/motor/recalcular/{id}` e
  aguardando a resposta (é rápido — spinner local, sem polling). Atualiza os KPIs do produto
  ao retornar.
  _Depende de: T-43_

- [ ] **T-51 — Estados de erro e falha parcial** `MVP`
  Tratar: `FALHOU` no status (motor indisponível → mensagem amigável, opção de retry);
  falha parcial (`produtosComFalha > 0` → aviso não-bloqueante "N produtos não recalculados");
  timeout/queda do polling (mensagem + botão "tentar de novo").
  _Depende de: T-48_

### Backend — lacunas identificadas na revisão (2026-07-12)

> Três lacunas apontadas na validação do orientador + o tratamento da omissão do `is_promocional`.
> A **T-54 (benchmark)** é a única com prioridade **IMEDIATA** — roda antes da confirmação do
> volume de SKUs e calibra a prioridade de todo o épico.

- [ ] **T-52 — Guard de concorrência do motor (409)** `MVP`
  Ponto único de proteção contra recálculos simultâneos: antes de chamar `processarLoteMotor()`,
  verificar o `MotorJobStatus` do estabelecimento e **rejeitar com `409 Conflict`** se já houver um
  job em andamento (estado `PROCESSANDO`). O guard vale para os **três gatilhos**, que passam todos
  por ele: manual (T-41), pós-importação (T-44) e cron mensal (T-35). Implementar como método/aspecto
  reutilizável (ex. `iniciarJobOuConflitar(estabelecimentoId)`), não duplicado em cada gatilho.
  - **Teste:** dois disparos concorrentes para o mesmo estabelecimento → o segundo recebe `409`.
  - **Teste:** disparo para estabelecimento diferente **não** é bloqueado (guard é por estabelecimento).
  _Depende de: T-40_
  ⚠️ Pré-requisito de qualquer gatilho múltiplo — implementar junto/antes de T-41, T-44 e T-35.

- [ ] **T-53 — Warm-up do Prophet no startup do ml-service** `MVP`
  Cobre o risco "cold start do Prophet" (compilação Stan na primeira chamada), hoje sem tarefa.
  Adicionar ao startup do FastAPI (evento `lifespan`/`startup`) uma **previsão dummy** com série
  sintética mínima, para que a primeira chamada real ao `/predict` não pague o custo de compilação
  nem estoure o `read-timeout` de 30 s do Feign.
  - Não deve derrubar a subida do serviço se falhar (log de aviso + segue).
  - Documentar no `ml-service/CLAUDE.md` (§ startup) e no README.
  _Depende de: —_ (serviço Python; independente do backend)
  ⚠️ Tarefa do **ml-service**, registrada aqui por pertencer ao Épico 7. Refletir no `ml-service/tasks.md`.

- [ ] **T-54 — Benchmark do lote (calibra a prioridade do épico)** `IMEDIATA`
  Script Python que **gera dados sintéticos** de vendas (90+ dias) para **50, 150 e 300 produtos**,
  dispara o lote atual (`POST /api/motor/recalcular` síncrono de hoje, T-23) e **mede o tempo total
  e o tempo médio por produto** em cada volume. Reusar `generate_synthetic_data.py` do ml-service.
  - **Objetivo:** substituir a estimativa "10–20+ min" por **número medido** e decidir com
    evidência se o Épico 7 é `MVP` ou `MVP-opcional`.
  - **Saída:** registrar os resultados numa **tabela em `docs/`** (ex.: `docs/benchmark-motor.md`) —
    será usada na **metodologia do TCC**.
  _Depende de: T-23 (já implementado), ml-service no ar_
  ✅ **Pode e deve rodar ANTES da confirmação do volume de SKUs** — é o que destrava a decisão.
  📝 **Esboço pronto (2026-07-12):** `ml-service/benchmark_motor.py` — mede N chamadas `/predict`
  sequenciais (custo dominante do lote), reusa `generate_synthetic_data.py`, faz warm-up do Prophet
  e grava a tabela em `docs/benchmark-motor.md`. **Só a sintaxe foi validada; falta EXECUTAR** com o
  ml-service no ar e o **Prophet ativo** (CmdStan — hoje quebrado localmente, ver SESSION.md). Se o
  Prophet estiver caído, o script mede só Holt-Winters e avisa que os números não são confiáveis.
  O caminho ponta a ponta via `POST /api/motor/recalcular` está como stub (`medir_e2e()`) para o
  número "oficial", se necessário.

- [ ] **T-55 — `is_promocional` no `montarRequest` (validade da comparação HW × Prophet)** `MVP`
  A omissão do `is_promocional` (o `MotorService.montarRequest` não popula o regressor) estava
  classificada como risco **baixo para carga**, mas é **ALTA para a validade acadêmica da
  comparação**: o regressor exógeno é uma **vantagem potencial do Prophet** que está sendo
  desligada silenciosamente. **Não deixar a omissão silenciosa.** Escolher **um** caminho:
  - **(a) Corrigir:** `montarRequest` passa a enviar `is_promocional` (a `Venda` já tem o campo);
    o ml-service usa o regressor no Prophet (ver `ml-service` T-10, hoje `MVP-opcional`). **OU**
  - **(b) Documentar explicitamente** na metodologia do TCC que a comparação roda **sem regressores
    exógenos** (ambos os modelos em igualdade de condições), registrando a limitação e a justificativa.
  _Depende de: T-21 (montarRequest) — e, se optar por (a), do regressor no ml-service_
  ⚠️ Decisão metodológica: alinhar com o orientador qual caminho seguir antes de fechar a redação do TCC.

---

## Pós-MVP

- [ ] **T-36 — `SugestaoCompraService` + Controller** `Pós-MVP`
  `GET /api/sugestao-compra`: produtos a repor agrupados por fornecedor com quantidade sugerida
  derivada do ponto de reposição. Alimenta a Tela 8.

- [ ] **T-37 — `ConfiguracoesController`** `Pós-MVP`
  `PUT /api/configuracoes/*`: atualizar nome fantasia, email e senha do estabelecimento. Tela 9.

- [ ] **T-38 — `POST /api/auth/reset`** `Pós-MVP`
  Recuperação de senha via email. Tela 1.

---

## Sumário

| Épico | Entrega | Tasks | Prioridade |
|---|---|---|---|
| 0 — Fundação | Infra transversal (pacotes, JWT dep., SecurityConfig temp, error handling) | T-01 → T-05 | MVP |
| 1 — Auth | `POST /api/auth/login` com JWT | T-06 → T-11 | MVP |
| 2 — Importação | `POST /api/importacao` com validação e persistência | T-12 → T-17 | MVP |
| 3 — Motor + ABC | `POST /api/motor/recalcular` com previsões e ABC | T-18 → T-25 | MVP |
| 4 — Produto | `/api/produtos/*` (4 endpoints) | T-26 → T-30 | MVP |
| 5 — Dashboard | `/api/alertas`, `/api/dashboard`, `/api/curva-abc` | T-31 → T-34 | MVP |
| 6 — Agendamento | Recálculo mensal automático | T-35 | MVP-opcional |
| 7 — Motor Assíncrono | Lote async + status + polling + lacunas da revisão (BE T-39→44,46,52→55 · FE T-47→51) | T-39 → T-55 | **SUSPENSO** (T-54 imediata) |
| Pós-MVP | Sugestão de compra, configurações, reset senha | T-36 → T-38 | Pós-MVP |

**54 tasks no total** (38 originais + 16 do Épico 7: 11 backend, 5 frontend; a antiga T-45 foi
**descartada** na validação e não conta). Épicos 0–6 em ordem estrita de dependência.
O Épico 7 está **SUSPENSO** (aguarda confirmação do volume de SKUs) — exceto a **T-54 (benchmark)**,
de prioridade **imediata**, que calibra a decisão. Evolui o Épico 3 (torna o lote da T-23
assíncrono); o scheduler (T-35) foi religado para reusar o núcleo da T-39 e passar pelo guard da T-52.

---

*Atualizar o status (`[ ]` → `[x]`) conforme as tasks forem concluídas.*
