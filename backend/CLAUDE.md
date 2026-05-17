# CLAUDE.md — Backend (Kotlin / Spring Boot)
> Instruções específicas do serviço `backend/`. Leia também o **CLAUDE.md na raiz** do monorepo antes de qualquer ação — as convenções gerais do projeto prevalecem.

---

## 1. Stack e Versões

| Componente | Versão |
|---|---|
| Kotlin | 1.9.25 |
| JVM target | Java 17 |
| Spring Boot | 3.3.4 |
| Spring Cloud | 2023.0.3 |
| Spring Cloud OpenFeign | gerenciado pelo BOM 2023.0.3 |

---

## 2. Dependências (`build.gradle.kts`)

### Produção
```kotlin
implementation("org.springframework.boot:spring-boot-starter-web")
implementation("org.springframework.boot:spring-boot-starter-data-jpa")
implementation("org.springframework.boot:spring-boot-starter-validation")
implementation("org.springframework.cloud:spring-cloud-starter-openfeign")
implementation("org.flywaydb:flyway-core")
implementation("org.flywaydb:flyway-mysql")
implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
implementation("org.jetbrains.kotlin:kotlin-reflect")
runtimeOnly("com.mysql:mysql-connector-j")
```

### Testes
```kotlin
testImplementation("org.springframework.boot:spring-boot-starter-test")
testImplementation("io.mockk:mockk:1.13.12")
testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
testRuntimeOnly("org.junit.platform:junit-platform-launcher")
```

> `flyway-core` e `flyway-mysql` são declarados explicitamente. O BOM do Spring Boot gerencia as versões — não pin manualmente.

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

```kotlin
@Service
class ProdutoService(
    private val produtoRepository: ProdutoRepository,
    private val mlServiceClient: MlServiceClient,
) {
    fun listarTodos(): List<ProdutoResponse> =
        produtoRepository.findAll().map { it.toResponse() }
}
```

### 3.3 Repository (`br.com.stocksense.repository`)
- Apenas `extends JpaRepository<Entidade, ID>` — sem lógica de negócio
- Queries derivadas ou `@Query` são aceitáveis; filtragem e transformação ficam no Service

```kotlin
interface ProdutoRepository : JpaRepository<Produto, Int>
```

### 3.4 Domain (`br.com.stocksense.domain`)
- Entidades JPA mapeando exatamente as tabelas do `V1__create_schema.sql`
- Campos calculados pelo motor preditivo (`classeAbc`, `pontoReposicao`, etc.) são `var nullable` — nunca recebidos via endpoint

```kotlin
@Entity
@Table(name = "produto")
class Produto(
    @Id
    @Column(name = "produto_id")
    val produtoId: Int,

    @Column(nullable = false, length = 100)
    var nome: String,

    @Column(name = "estoque_atual", nullable = false)
    var estoqueAtual: Int,

    @Column(name = "nivel_servico_alvo", precision = 5, scale = 2)
    var nivelServicoAlvo: BigDecimal = BigDecimal("0.95"),

    // campos calculados pelo motor — nunca recebidos via planilha
    @Column(name = "classe_abc", length = 1)
    var classeAbc: String? = null,

    @Column(name = "ponto_reposicao", precision = 10, scale = 2)
    var pontoReposicao: BigDecimal? = null,

    @Column(name = "data_ultimo_calculo")
    var dataUltimoCalculo: LocalDateTime? = null,
)
```

### 3.5 DTO (`br.com.stocksense.dto`)
- Subpacotes `request/` e `response/`
- Validações Bean Validation ficam **no DTO Request** com `@field:`

```kotlin
// dto/request/ProdutoRequest.kt
data class ProdutoRequest(
    @field:NotNull
    val produtoId: Int,

    @field:NotBlank
    @field:Size(max = 100)
    val nome: String,

    @field:Min(0)
    val estoqueAtual: Int,

    @field:DecimalMin("0.0")
    @field:DecimalMax("1.0")
    val nivelServicoAlvo: BigDecimal = BigDecimal("0.95"),
)

// dto/response/ProdutoResponse.kt
data class ProdutoResponse(
    val produtoId: Int,
    val nome: String,
    val estoqueAtual: Int,
    val nivelServicoAlvo: BigDecimal,
    val classeAbc: String?,
    val pontoReposicao: BigDecimal?,
    val diasAteRuptura: Int?,
    val dataUltimoCalculo: LocalDateTime?,
)
```

---

## 4. Feign Client (`br.com.stocksense.client`)

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

### Tratamento de FeignException no Service

```kotlin
fun executarMotor(produtoId: Int): PredictResponse {
    return try {
        mlServiceClient.predict(buildRequest(produtoId))
    } catch (ex: FeignException) {
        log.error("Falha ao chamar AI/ML Service para produto {}", produtoId, ex)
        throw MotorPreditivoException("Serviço de previsão indisponível. Tente novamente em instantes.")
    }
}
```

- `log.error` com o stack trace completo — **apenas no log**
- A exception de domínio (`MotorPreditivoException`) é capturada pelo `GlobalExceptionHandler`

---

## 5. Tratamento de Erros (`br.com.stocksense.exception`)

### GlobalExceptionHandler

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {

    private val log = LoggerFactory.getLogger(javaClass)

    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidation(ex: MethodArgumentNotValidException): ProblemDetail {
        val detail = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Dados de entrada inválidos")
        detail.setProperty("campos", ex.bindingResult.fieldErrors.map {
            mapOf("campo" to it.field, "erro" to it.defaultMessage)
        })
        return detail
    }

    @ExceptionHandler(EntityNotFoundException::class)
    fun handleNotFound(ex: EntityNotFoundException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.message ?: "Recurso não encontrado")

    @ExceptionHandler(MotorPreditivoException::class)
    fun handleMotor(ex: MotorPreditivoException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.BAD_GATEWAY, ex.message ?: "Erro no motor preditivo")

    @ExceptionHandler(Exception::class)
    fun handleGeneric(ex: Exception): ProblemDetail {
        log.error("Erro inesperado não tratado", ex)
        return ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR,
            "Erro interno. Contate o suporte."
        )
    }
}
```

- Todas as respostas de erro seguem **RFC 7807** (`application/problem+json`)
- Stack trace **nunca** vai no body da resposta — apenas no log interno

---

## 6. Migrations Flyway

### Localização
`src/main/resources/db/migration/`

### Nomenclatura dos arquivos
| Arquivo | Propósito |
|---|---|
| `V1__create_schema.sql` | Schema inicial — todas as tabelas |
| `V2__<descricao>.sql` | Próxima alteração incremental |

**Nunca altere** um arquivo de migration já commitado — crie sempre uma nova versão.

### Regras obrigatórias no DDL
```sql
-- Declarar ENGINE, CHARSET e COLLATE em toda tabela
CREATE TABLE venda (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT      NOT NULL,
    data_hora  DATETIME NOT NULL,           -- DATETIME, nunca TIMESTAMP
    quantidade INT      NOT NULL,
    CONSTRAINT fk_venda_produto
        FOREIGN KEY (produto_id) REFERENCES produto (produto_id)
        ON DELETE RESTRICT                  -- declarar ON DELETE explicitamente
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
```

---

## 7. Convenções de Nomenclatura

| Artefato | Padrão | Exemplo |
|---|---|---|
| Pacote raiz | `br.com.stocksense` | — |
| Entidade JPA | PascalCase, sem sufixo | `Produto`, `Venda` |
| DTO de entrada | sufixo `Request` | `ProdutoRequest` |
| DTO de saída | sufixo `Response` | `ProdutoResponse` |
| Repository | sufixo `Repository` | `ProdutoRepository` |
| Service | sufixo `Service` | `ProdutoService` |
| Controller | sufixo `Controller` | `ProdutoController` |
| Feign Client | sufixo `Client` | `MlServiceClient` |
| Exception de domínio | sufixo `Exception` | `MotorPreditivoException` |
| Migration Flyway | `V{n}__{descricao_snake}.sql` | `V2__add_coluna_sku.sql` |
| Configs de bean | sufixo `Config` | `FeignConfig`, `FlywayConfig` |

---

## 8. O que NUNCA fazer neste serviço

| ❌ Proibido | ✅ Correto |
|---|---|
| Lógica de negócio no Controller | Delegar integralmente ao Service |
| Retornar entidade JPA no endpoint | Mapear para DTO Response |
| Hardcodar URL, senha ou credencial | `application.yml` + variável de ambiente |
| Usar `SERIAL` ou `SERIAL PRIMARY KEY` | `INT AUTO_INCREMENT PRIMARY KEY` (MySQL 8.0) |
| Usar `TIMESTAMP` para colunas de data/hora | `DATETIME` |
| Omitir `utf8mb4` no DDL | Declarar `CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci` |
| Alterar migration já commitada | Criar nova migration `V{n+1}__...sql` |
| Vazar stack trace para o cliente | Log interno + `ProblemDetail` genérico |
| Chamar Repository diretamente no Controller | Acessar apenas via Service |
| Hardcodar `ml.service.url` no código | Ler de `\${ml.service.url}` no `@FeignClient` |
| Aceitar campos calculados pelo motor via endpoint | Rejeitar `classeAbc`, `pontoReposicao`, `estoqueSeguranca` na entrada |
