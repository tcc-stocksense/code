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

- [ ] **T-05 — Acordo cross-service: `desvio_padrao_demanda` no ml-service** `MVP`
  ⚠️ **Não é código — é um alinhamento com o time.**
  O ml-service precisa adicionar `desvio_padrao_demanda: float` ao `PredictResponse`
  antes de implementar T-30 (detalhe do produto, Épico 4).
  Registrar a decisão e atualizar o CLAUDE.md do ml-service quando confirmado.
  _Não bloqueia os épicos 1–3, bloqueia T-30._

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

> Entrega: `POST /api/importacao` processando `.xlsx` e persistindo no banco.
> Sem motor ainda — apenas carga de dados.

- [ ] **T-12 — Entidades de importação + Repositories** `MVP` / `MVP-opcional`
  **MVP:** `Produto` (todos os campos do V1, calculados como `var nullable`),
  `Venda` (`id` auto, `produtoId`, `dataHora: LocalDateTime`, `quantidade`, `valorVenda?`, `isPromocional`).
  **MVP-opcional:** `Fornecedor` (PK natural, sem `@GeneratedValue`),
  `ProdutoFornecedor` (chave composta `@EmbeddedId`, `leadTimeMedio`, `variabilidadeLeadTime`).
  Repositories: `ProdutoRepository`, `VendaRepository`, `FornecedorRepository`,
  `ProdutoFornecedorRepository`.
  FK de `Produto` → `Estabelecimento` (do Épico 1).
  _Depende de: T-06_

- [ ] **T-13 — DTOs de produto e importação** `MVP`
  `ProdutoResponse` (todos os campos incluindo calculados nullable).
  `ProdutoEstoqueRequest(@field:Min(0) estoqueAtual: Int)`.
  `ImportacaoResponse` (lista de `{ planilha, linhas_processadas, status, erros[] }` por bloco).
  Campos calculados (`classeAbc`, `pontoReposicao`, etc.) **nunca** aparecem em request.
  _Depende de: T-01_

- [ ] **T-14 — `ImportacaoService` — parsing e validação** `MVP`
  Recebe `MultipartFile` (`.xlsx`). Usa Apache POI para ler:
  - `2_produtos` (obrigatória): `produto_id` único e inteiro, `nome` e `estoque_atual` presentes
  - `5_vendas` (obrigatória): `produto_id` existe em produtos, data ISO `YYYY-MM-DD`,
    `quantidade > 0`, decimais com ponto, mínimo 90 dias de histórico
  - `1_estabelecimento`, `3_fornecedores`, `4_produto_fornecedor` (desejáveis):
    processar se presentes; se ausentes, aplicar defaults (`fornecedor_id = 1`,
    `lead_time_medio = 3`, `variabilidade_lead_time = 1.0`)
  Acumular todos os erros e lançar `ImportacaoException(erros)` ao final — nunca parar no primeiro.
  _Depende de: T-04, T-12, T-13_

- [ ] **T-15 — `ImportacaoService` — persistência** `MVP`
  Após validação sem erros: persistir em ordem (produtos antes de vendas por FK).
  Retornar `ImportacaoResponse` com status por bloco.
  _Depende de: T-14_

- [ ] **T-16 — `ImportacaoController`** `MVP`
  `POST /api/importacao` (multipart/form-data, campo `file`).
  Retorna `ImportacaoResponse`. Zero lógica no controller.
  _Depende de: T-04, T-15_

- [ ] **T-17 — Testes unitários: `ImportacaoService`** `MVP`
  Cenários: planilha válida, `produto_id` duplicado, data em formato errado,
  `quantidade ≤ 0`, histórico com < 90 dias, `produto_id` de venda inexistente em produtos,
  planilhas desejáveis ausentes (defaults aplicados).
  _Depende de: T-15_

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
  estoqueSeguranca, diasAteRuptura?, aviso?)`.
  _Depende de: T-01_
  Mapeamento snake_case via `@JsonNaming` (sem mexer no ObjectMapper global).
  ⚠️ `desvioPadraoDemanda` **fora do contrato** — o ml-service não o devolve (T-05 pendente).
  ⚠️ `@JsonIgnoreProperties(ignoreUnknown = true)`: o ml-service ainda devolve `classe_abc`
  e `abc_proxy` (dívida técnica — deveriam ter saído de lá na ADR #3); o backend os ignora.

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
  ⚠️ `desvioPadraoDemanda` não é atualizado (o motor não o devolve — T-05).

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

- [ ] **T-26 — `ProdutoService` — listagem e edição de estoque** `MVP`
  `listarTodos(estabelecimentoId: Int): List<ProdutoResponse>`
  `atualizarEstoque(produtoId: Int, estoqueAtual: Int): ProdutoResponse`
  Lançar `RecursoNaoEncontradoException` se produto não encontrado.
  _Depende de: T-04, T-12, T-13_

- [ ] **T-27 — `ProdutoService` — detalhe do produto** `MVP`
  DTO: `ProdutoDetalheResponse` com KPIs calculados (`pontoReposicao`, `estoqueSeguranca`,
  `diasAteRuptura`, `desvioPadraoDemanda`), demanda média diária
  (calculada de `venda`: `SUM(quantidade) / dias_de_historico`) e série de previsão
  mais recente (últimas 30 linhas de `previsao` pelo maior `executadoEm`).
  `detalhe(produtoId: Int): ProdutoDetalheResponse`
  ⚠️ Depende de T-05 (ml-service retornando `desvio_padrao_demanda`).
  _Depende de: T-04, T-12, T-18, T-21_

- [ ] **T-28 — `MetricaService` — comparativo de modelos** `MVP`
  DTO: `MetricaResponse(modelo, mape, rmse, mae, selecionado, executadoEm)`.
  `metricas(produtoId: Int): List<MetricaResponse>`: retorna as 2 linhas mais recentes
  de `metrica_modelo` para o produto (pelo maior `executadoEm`) — alimenta a Tela 10.
  Lançar `RecursoNaoEncontradoException` se produto não encontrado.
  _Depende de: T-04, T-18_

- [ ] **T-29 — `ProdutoController`** `MVP`
  Todos os endpoints de produto em um único controller:
  - `GET /api/produtos` → `listarTodos()`
  - `PATCH /api/produtos/{id}/estoque` → `atualizarEstoque()` com `@Valid @RequestBody`
  - `GET /api/produtos/{id}/detalhe` → `detalhe()`
  - `GET /api/produtos/{id}/metricas` → `metricas()`
  _Depende de: T-04, T-26, T-27, T-28_

- [ ] **T-30 — Testes unitários: `ProdutoService`** `MVP`
  Cenários: listagem retorna lista correta, edição de estoque atualiza apenas o campo,
  produto não encontrado → exception, detalhe calcula demanda média corretamente.
  _Depende de: T-26, T-27_

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
  Chama `MotorService.executarMotor()` para cada produto ativo do estabelecimento,
  depois `AbcService.recalcularAbc()`. Logar início, fim e quantidade processada.
  _Depende de: T-21, T-22_

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
| Pós-MVP | Sugestão de compra, configurações, reset senha | T-36 → T-38 | Pós-MVP |

**38 tasks no total.** Épicos em ordem estrita de dependência — não pular.

---

*Atualizar o status (`[ ]` → `[x]`) conforme as tasks forem concluídas.*
