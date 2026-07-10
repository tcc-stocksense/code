# CLAUDE.md — Backend (Kotlin / Spring Boot)
> Instruções específicas do serviço `backend/`. Leia também o **CLAUDE.md na raiz** do monorepo antes de qualquer ação — as convenções gerais do projeto prevalecem.

---

## Como rodar o backend localmente

Pré-requisito: Docker Desktop aberto e rodando, e um `.env` na **raiz do monorepo**
(não em `backend/`) com `DB_ROOT_PASSWORD`, `DB_USERNAME`, `DB_PASSWORD`.

```bash
# 1. Sobe só o MySQL (não precisa do ml-service/frontend pra rodar o backend)
docker-compose up -d db

# 2. Roda o backend com as mesmas credenciais do .env
cd backend
DB_URL="jdbc:mysql://localhost:3307/stocksense?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true" \
DB_USERNAME=<valor do DB_USERNAME no .env> \
DB_PASSWORD=<valor do DB_PASSWORD no .env> \
./gradlew bootRun
```

O Flyway aplica as migrations automaticamente na subida (schema + seed). API em `http://localhost:8080`.

**Se o Flyway falhar com `Migration checksum mismatch`:** o volume do MySQL tem uma
versão antiga de uma migration já aplicada (schema desatualizado ou trocado
manualmente). Resolver derrubando o volume e recriando o banco do zero:

```bash
docker-compose down -v
docker-compose up -d db
```

---

## Prioridade MVP — mapa de entregáveis

Status: **MVP** (núcleo da entrega) · **MVP-opcional** (funciona sem, agrega valor) · **Pós-MVP** · **Movido/Novo**.

### Endpoints REST

| Método | Rota | Funcionalidade / Tela | Prioridade |
|---|---|---|---|
| POST | `/api/auth/login` | Login no estabelecimento (T1) | **MVP** |
| POST | `/api/importacao` | Ingestão de planilhas `.xlsx` (T3) | **MVP** |
| POST | `/api/motor/recalcular` | Dispara o motor para todos os produtos (demo + cron) | **MVP** |
| GET | `/api/produtos` | Lista de estoque (T4) | **MVP** |
| PATCH | `/api/produtos/{id}/estoque` | Edição manual de estoque (T4) | **MVP** |
| GET | `/api/produtos/{id}/detalhe` | Detalhe + estatísticas (T6) | **MVP** |
| GET | `/api/produtos/{id}/metricas` | Comparativo Holt-Winters × Prophet (T10) | **MVP** |
| GET | `/api/dashboard` | KPIs e série de faturamento (T2) | **MVP** |
| GET | `/api/alertas` | Reposição por urgência (T5) | **MVP** |
| GET | `/api/curva-abc` | Curva ABC / Pareto (T7) | **MVP** |
| GET/POST | `/api/sugestao-compra` | Pedido por fornecedor (T8) | **Pós-MVP** |
| PUT | `/api/configuracoes/*` | Estabelecimento / notificações (T9) | **Pós-MVP** |
| POST | `/api/auth/reset` | Recuperação de senha (T1) | **Pós-MVP** |

### Services / regras

| Service | Responsabilidade | Prioridade |
|---|---|---|
| `ImportacaoService` | Parsing `.xlsx`, validação de schema, persistência | **MVP** |
| `MotorService` | Aciona ML, persiste `previsao` + `metrica_modelo`, atualiza `produto` | **MVP** |
| `AbcService` | Classificação ABC (ranking por faturamento) — **veio do ml-service** | **MVP** |
| `ProdutoService` | CRUD + leitura de estoque | **MVP** |
| `DashboardService` / `AlertaService` | Agregações de urgência e KPIs | **MVP** |
| `AuthService` | Login no estabelecimento (BCrypt) | **MVP** |
| Agendamento `@Scheduled` mensal | Recálculo automático | **MVP-opcional** |
| `SugestaoCompraService` | Pedido por fornecedor | **Pós-MVP** |

### Entidades (espelham o `V1__create_schema.sql`)

| Entidade | Tabela | Status | Prioridade |
|---|---|---|---|
| `Estabelecimento` | `estabelecimento` (com login) | **Nova** (login embutido) | **MVP** |
| `Produto` | `produto` | Existente (+ `estabelecimento_id`) | **MVP** |
| `Venda` | `venda` | Existente | **MVP** |
| `Previsao` | `previsao` | **Alterada** (sem métricas) | **MVP** |
| `MetricaModelo` | `metrica_modelo` | **Nova** | **MVP** |
| `Fornecedor` | `fornecedor` | Nova | **MVP-opcional** |
| `ProdutoFornecedor` | `produto_fornecedor` | Nova | **MVP-opcional** |

---

## 1. Stack e Versões

| Componente | Versão |
|---|---|
| Kotlin | 1.9.25 |
| JVM target | Java 17 |
| Spring Boot | 3.3.4 |
| Spring Cloud | 2023.0.3 |
| Spring Cloud OpenFeign | gerenciado pelo BOM 2023.0.3 |
| Banco de dados | MySQL 8.0 |

---

## 2. Dependências (`build.gradle.kts`)

### Produção
```kotlin
implementation("org.springframework.boot:spring-boot-starter-web")
implementation("org.springframework.boot:spring-boot-starter-data-jpa")
implementation("org.springframework.boot:spring-boot-starter-validation")
implementation("org.springframework.boot:spring-boot-starter-security")   // login (T1)
implementation("org.springframework.cloud:spring-cloud-starter-openfeign")
implementation("org.flywaydb:flyway-core")
implementation("org.flywaydb:flyway-mysql")
implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
implementation("org.jetbrains.kotlin:kotlin-reflect")
implementation("org.apache.poi:poi-ooxml:5.3.0")                          // leitura de .xlsx (T3)
runtimeOnly("com.mysql:mysql-connector-j")
```

### Testes
```kotlin
testImplementation("org.springframework.boot:spring-boot-starter-test")
testImplementation("org.springframework.security:spring-security-test")
testImplementation("io.mockk:mockk:1.13.12")
testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
testRuntimeOnly("org.junit.platform:junit-platform-launcher")
```

> **Adicionadas:** `spring-boot-starter-security` (login no estabelecimento) e `poi-ooxml` (parsing das planilhas de importação). `flyway-core` e `flyway-mysql` continuam declarados explicitamente; o BOM do Spring Boot gerencia as versões — não pin manualmente.

---

## 3. Arquitetura em Camadas

```
Controller → Service → Repository (JpaRepository)
                ↓
          MlServiceClient (Feign → AI/ML Service)
```

### 3.1 Controller (`br.com.stocksense.controller`)
- Recebe a requisição HTTP, valida entrada via `@Valid` (Bean Validation)
- Delega **toda** a lógica ao Service — zero acesso direto a Repository
- Retorna sempre um DTO Response — nunca entidade JPA

```kotlin
@RestController
@RequestMapping("/api/produtos")
class ProdutoController(private val produtoService: ProdutoService) {

    @GetMapping
    fun listar(): List<ProdutoResponse> = produtoService.listarTodos()

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun criar(@Valid @RequestBody request: ProdutoRequest): ProdutoResponse =
        produtoService.criar(request)
}
```

### 3.2 Service (`br.com.stocksense.service`)
- Contém **toda** a lógica de negócio
- Único ponto que chama Repository e `MlServiceClient`
- Responsável pelo mapeamento entidade ↔ DTO
- Trata `FeignException` e relança como exceção de domínio com mensagem amigável

### 3.3 Repository (`br.com.stocksense.repository`)
- Apenas `extends JpaRepository<Entidade, ID>` — sem lógica de negócio
- Queries derivadas ou `@Query` são aceitáveis; filtragem e transformação ficam no Service

```kotlin
interface ProdutoRepository : JpaRepository<Produto, Int>
interface PrevisaoRepository : JpaRepository<Previsao, Int>
interface MetricaModeloRepository : JpaRepository<MetricaModelo, Int>
```

### 3.4 Domain (`br.com.stocksense.domain`)
- Entidades JPA mapeando exatamente as tabelas do `V1__create_schema.sql`
- Campos calculados pelo motor (`pontoReposicao`, `estoqueSeguranca`, etc.) são `var nullable` — nunca recebidos via endpoint
- `classeAbc` é calculado pelo `AbcService` (backend), não vem mais do ml-service

```kotlin
@Entity
@Table(name = "produto")
class Produto(
    @Id
    @Column(name = "produto_id")
    val produtoId: Int,

    @Column(name = "estabelecimento_id", nullable = false)
    var estabelecimentoId: Int = 1,

    @Column(nullable = false, length = 100)
    var nome: String,

    @Column(name = "estoque_atual", nullable = false)
    var estoqueAtual: Int,

    @Column(name = "nivel_servico_alvo", precision = 5, scale = 2)
    var nivelServicoAlvo: BigDecimal = BigDecimal("0.95"),

    // campos calculados — nunca recebidos via planilha
    @Column(name = "classe_abc", length = 1)
    var classeAbc: String? = null,            // setado pelo AbcService

    @Column(name = "desvio_padrao_demanda", precision = 10, scale = 4)
    var desvioPadraoDemanda: BigDecimal? = null,  // setado pelo MotorService a partir do PredictResponse (§4)

    @Column(name = "ponto_reposicao", precision = 10, scale = 2)
    var pontoReposicao: BigDecimal? = null,

    @Column(name = "estoque_seguranca", precision = 10, scale = 2)
    var estoqueSeguranca: BigDecimal? = null,

    @Column(name = "data_ultimo_calculo")
    var dataUltimoCalculo: LocalDateTime? = null,
)
```

```kotlin
@Entity
@Table(name = "estabelecimento")
class Estabelecimento(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int? = null,

    @Column(name = "nome_fantasia", nullable = false, length = 100)
    var nomeFantasia: String,

    @Column(length = 18) var cnpj: String? = null,
    @Column(length = 200) var endereco: String? = null,

    // login do MVP — uma credencial por estabelecimento
    @Column(nullable = false, length = 100, unique = true)
    var email: String,

    @Column(name = "senha_hash", nullable = false, length = 255)
    var senhaHash: String,
)
```

```kotlin
@Entity
@Table(name = "previsao")
class Previsao(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int? = null,

    @Column(name = "produto_id", nullable = false) val produtoId: Int,
    @Column(name = "data_previsao", nullable = false) val dataPrevisao: LocalDate,
    @Column(name = "quantidade_prevista", precision = 10, scale = 2) val quantidadePrevista: BigDecimal?,
    @Column(name = "modelo_utilizado", length = 50) val modeloUtilizado: String?,
    @Column(name = "executado_em", nullable = false) val executadoEm: LocalDateTime,
)
```

```kotlin
@Entity
@Table(name = "metrica_modelo")
class MetricaModelo(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int? = null,

    @Column(name = "produto_id", nullable = false) val produtoId: Int,
    @Column(length = 50, nullable = false) val modelo: String,      // 'holt_winters' | 'prophet'
    @Column(precision = 8, scale = 4) val mape: BigDecimal?,
    @Column(precision = 10, scale = 4) val rmse: BigDecimal?,
    @Column(precision = 10, scale = 4) val mae: BigDecimal?,
    @Column(nullable = false) val selecionado: Boolean = false,
    @Column(name = "executado_em", nullable = false) val executadoEm: LocalDateTime,
)
```

> **Demais entidades** (`Venda`, `Fornecedor`, `ProdutoFornecedor`) seguem o mesmo padrão, mapeando 1:1 as colunas do `V1`. `Venda` inclui `valorVenda: BigDecimal?` e `isPromocional: Int`.

### 3.5 DTO (`br.com.stocksense.dto`)
- Subpacotes `request/` e `response/`
- Validações Bean Validation ficam **no DTO Request** com `@field:`
- O endpoint de produto **rejeita** campos calculados (`classeAbc`, `pontoReposicao`, `estoqueSeguranca`, `desvioPadraoDemanda`) — não aparecem no `ProdutoRequest`

---

## 4. Feign Client (`br.com.stocksense.client`) e o Motor

### Interface

```kotlin
@FeignClient(name = "ml-service", url = "\${ml.service.url}")
interface MlServiceClient {

    @PostMapping("/predict")
    fun predict(@RequestBody request: PredictRequest): PredictResponse

    @GetMapping("/health")
    fun health(): Map<String, String>
}
```

### Contrato `PredictResponse` (espelha o ml-service)

```kotlin
data class PredictResponse(
    val produtoId: Int,
    val modeloSelecionado: String,                 // "holt_winters" | "prophet"
    val previsoes: List<PrevisaoDiaria>,           // 30 pontos
    val metricas: Map<String, MetricasModelo>,     // { "holt_winters": {...}, "prophet": {...} }
    val pontoReposicao: BigDecimal,
    val estoqueSeguranca: BigDecimal,
    val diasAteRuptura: BigDecimal?,               // null quando demanda média = 0
    val desvioPadraoDemanda: BigDecimal?,          // σ da demanda — alimenta produto.desvioPadraoDemanda e a Tela 6
    val aviso: String? = null,                     // MAPE > 50%
)
```

> **Mudou:** o `PredictResponse` **não tem mais `classeAbc`** (ABC virou responsabilidade do backend). `diasAteRuptura` é nullable e há o campo `aviso`. **`desvioPadraoDemanda` foi adicionado** (T-05 resolvido em 2026-07-10) — o `MotorService` grava esse valor em `produto.desvioPadraoDemanda` a cada execução.

### Persistência do resultado do motor (`MotorService`)

Para cada produto, ao receber o `PredictResponse`, persistir **numa transação**:
- **30 linhas** em `previsao` (uma por `PrevisaoDiaria`), todas com o mesmo `executadoEm` e `modeloUtilizado = modeloSelecionado`;
- **2 linhas** em `metrica_modelo` (uma por modelo em `metricas`), com `selecionado = (modelo == modeloSelecionado)`;
- atualizar em `produto`: `pontoReposicao`, `estoqueSeguranca`, `dataUltimoCalculo = now`.

```kotlin
@Service
class MotorService(
    private val produtoRepository: ProdutoRepository,
    private val vendaRepository: VendaRepository,
    private val previsaoRepository: PrevisaoRepository,
    private val metricaRepository: MetricaModeloRepository,
    private val mlServiceClient: MlServiceClient,
) {
    @Transactional
    fun executarMotor(produtoId: Int) {
        val resp = try {
            mlServiceClient.predict(montarRequest(produtoId))
        } catch (ex: FeignException) {
            log.error("Falha ao chamar AI/ML Service para produto {}", produtoId, ex)
            throw MotorPreditivoException("Serviço de previsão indisponível. Tente novamente em instantes.")
        }
        val agora = LocalDateTime.now()
        previsaoRepository.saveAll(resp.previsoes.map { it.toEntity(produtoId, resp.modeloSelecionado, agora) })
        metricaRepository.saveAll(resp.metricas.map { (modelo, m) ->
            m.toEntity(produtoId, modelo, modelo == resp.modeloSelecionado, agora)
        })
        atualizarProduto(produtoId, resp, agora)
    }
}
```

### Timeout (`application.yml`)

```yaml
spring:
  cloud:
    openfeign:
      client:
        config:
          ml-service:
            connect-timeout: 5000    # 5 s — handshake TCP
            read-timeout: 30000      # 30 s — o motor Python pode demorar
```

O nome `ml-service` em `config:` deve ser idêntico ao `name =` no `@FeignClient`.

> ### ✅ Decisão tomada — fonte de `desvio_padrao_demanda` e da variabilidade da T6
> Resolvido em 2026-07-10: o ml-service passou a devolver `desvio_padrao_demanda` no `PredictResponse` (opção *a*, como recomendado — fonte única, sem recalcular no backend). O `MotorService` grava o valor em `produto.desvioPadraoDemanda` a cada `executarMotor()`. A Tela 6 já pode consumir esse campo para exibir a variabilidade (σ + CV).

---

## 5. Importação de Planilhas (`ImportacaoService`) — Tela 3

Núcleo do MVP. Recebe `.xlsx` via multipart, valida pelo **Guia de Importação v2.0** e persiste.

- **Endpoint:** `POST /api/importacao` (multipart). Planilhas **obrigatórias**: `2_produtos`, `5_vendas`. **Desejáveis**: `1_estabelecimento`, `3_fornecedores`, `4_produto_fornecedor`.
- **Parsing:** Apache POI (`poi-ooxml`).
- **Validações (rejeitar com `400` + lista de erros):** `produto_id` único e inteiro; `data` em ISO `YYYY-MM-DD`; `quantidade > 0`; decimais com ponto; todo `produto_id` de vendas existe em produtos; mínimo de 90 dias de histórico.
- **Defaults quando desejáveis ausentes:** vincular produtos ao **Fornecedor Padrão** (seed `V2`, `fornecedor_id = 1`) → `lead_time_medio = 3`, `variabilidade_lead_time = 1.0` (defaults do schema).
- **Resposta:** `{ planilha, linhas_processadas, status, erros[] }` por bloco.

> Após uma importação bem-sucedida, o backend deve disparar o `MotorService` (recálculo) para os produtos afetados, ou orientar o gestor a acionar `POST /api/motor/recalcular`.

---

## 6. Classificação ABC (`AbcService`) — veio do ml-service

ABC é ranking **relativo entre todos os produtos** do estabelecimento — por isso vive no backend, que tem o catálogo inteiro e o `valor_venda`.

```
1. SELECT produto_id, SUM(valor_venda) AS faturamento
     FROM venda v JOIN produto p ...
    WHERE p.estabelecimento_id = ?
    GROUP BY produto_id
    ORDER BY faturamento DESC
2. Calcular % acumulada do faturamento total
3. Atribuir: A (acumulado <= 80%), B (<= 95%), C (resto)
4. UPDATE produto SET classe_abc = ?
```

- **Fallback:** quando `valor_venda` é nulo em parte do histórico (campo "Recomendado", não obrigatório no Guia), usar `quantidade` como proxy do faturamento e **documentar a limitação** na resposta (`abc_proxy = true`).
- Executado junto do recálculo mensal (`@Scheduled`) e exposto também via `POST /api/motor/recalcular` para demonstração.

---

## 7. Autenticação — Login no Estabelecimento (T1)

Decisão: **login por estabelecimento** (uma credencial por mercado), sem tabela `usuario` no MVP. Consequência aceita: não há separação de perfil entre "Gestor" e "Equipe Técnica" — a Tela 10 compartilha a mesma sessão autenticada. Separação por perfil é evolução futura (aditiva).

- `email` + `senha_hash` ficam na entidade `Estabelecimento`.
- Hash com **BCrypt** (`PasswordEncoder` do Spring Security).
- `POST /api/auth/login` valida e emite o token de sessão.

> ### ⚠ Decisão pendente — mecanismo de sessão
> Para o MVP recomendo **JWT stateless** (simples de consumir pelo front JS) ou, se quiserem o mínimo absoluto, **HTTP Basic**. Como login não é o foco do TCC, qualquer um é defensável — só precisa escolher um e documentar. (Não adicionei dependência de JWT ainda para não fixar a decisão.)

---

## 8. Tratamento de Erros (`br.com.stocksense.exception`)

Mantido como antes — todas as respostas de erro seguem **RFC 7807** (`application/problem+json`); stack trace **nunca** vai no body, apenas no log.

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {
    private val log = LoggerFactory.getLogger(javaClass)

    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidation(ex: MethodArgumentNotValidException): ProblemDetail { /* ... 400 + campos */ }

    @ExceptionHandler(EntityNotFoundException::class)
    fun handleNotFound(ex: EntityNotFoundException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.message ?: "Recurso não encontrado")

    @ExceptionHandler(MotorPreditivoException::class)
    fun handleMotor(ex: MotorPreditivoException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.BAD_GATEWAY, ex.message ?: "Erro no motor preditivo")

    @ExceptionHandler(ImportacaoException::class)   // novo: erros de validação de planilha
    fun handleImportacao(ex: ImportacaoException): ProblemDetail {
        val detail = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Falha na importação")
        detail.setProperty("erros", ex.erros)
        return detail
    }

    @ExceptionHandler(Exception::class)
    fun handleGeneric(ex: Exception): ProblemDetail {
        log.error("Erro inesperado não tratado", ex)
        return ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "Erro interno. Contate o suporte.")
    }
}
```

> **Adicionado** `ImportacaoException` → `400` com a lista de erros de validação das planilhas.

---

## 9. Migrations Flyway

### Localização
`src/main/resources/db/migration/`

### Estado atual
| Arquivo | Propósito |
|---|---|
| `V1__create_schema.sql` | Schema completo (consolidado) — **congelado** |
| `V2__seed_dados_padrao.sql` | Estabelecimento e fornecedor padrão (seed) |
| `V3__<descricao>.sql` | Próxima alteração incremental |

**Nunca altere** uma migration já commitada — crie sempre uma nova versão. O `V1` foi consolidado enquanto o projeto era 100% local; a partir daqui a regra vale integralmente.

### Regras obrigatórias no DDL
- Declarar `ENGINE = InnoDB`, `CHARSET = utf8mb4`, `COLLATE = utf8mb4_unicode_ci` em toda tabela.
- `DATETIME`, nunca `TIMESTAMP`.
- `INT AUTO_INCREMENT PRIMARY KEY` (MySQL 8.0), nunca `SERIAL`.
- Declarar `ON DELETE` explicitamente em toda FK (mestre/histórico = `RESTRICT`; derivado/elo = `CASCADE`).

---

## 10. Convenções de Nomenclatura

| Artefato | Padrão | Exemplo |
|---|---|---|
| Pacote raiz | `br.com.stocksense` | — |
| Entidade JPA | PascalCase, sem sufixo | `Produto`, `MetricaModelo` |
| DTO de entrada | sufixo `Request` | `ProdutoRequest` |
| DTO de saída | sufixo `Response` | `ProdutoResponse` |
| Repository | sufixo `Repository` | `PrevisaoRepository` |
| Service | sufixo `Service` | `MotorService`, `AbcService` |
| Controller | sufixo `Controller` | `ImportacaoController` |
| Feign Client | sufixo `Client` | `MlServiceClient` |
| Exception de domínio | sufixo `Exception` | `MotorPreditivoException`, `ImportacaoException` |
| Migration Flyway | `V{n}__{descricao_snake}.sql` | `V3__add_tabela_pedido.sql` |
| Configs de bean | sufixo `Config` | `FeignConfig`, `SecurityConfig` |

---

## 11. O que NUNCA fazer neste serviço

| ❌ Proibido | ✅ Correto |
|---|---|
| Lógica de negócio no Controller | Delegar integralmente ao Service |
| Retornar entidade JPA no endpoint | Mapear para DTO Response |
| Hardcodar URL, senha ou credencial | `application.yml` + variável de ambiente |
| Usar `SERIAL` | `INT AUTO_INCREMENT PRIMARY KEY` (MySQL 8.0) |
| Usar `TIMESTAMP` para data/hora | `DATETIME` |
| Omitir `utf8mb4` ou `ON DELETE` no DDL | Declarar charset/collate e `ON DELETE` |
| Alterar migration já commitada | Criar nova migration `V{n+1}__...sql` |
| Vazar stack trace para o cliente | Log interno + `ProblemDetail` genérico |
| Chamar Repository direto no Controller | Acessar apenas via Service |
| Aceitar campos calculados via endpoint | Rejeitar `classeAbc`, `pontoReposicao`, `estoqueSeguranca`, `desvioPadraoDemanda` |
| Persistir senha em texto puro | BCrypt (`PasswordEncoder`) |
| Pedir ABC ao ml-service | Calcular no `AbcService` (backend tem o catálogo) |
| Esperar `classeAbc` no `PredictResponse` | Vem do `AbcService`, não do motor |
