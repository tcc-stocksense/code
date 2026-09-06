# Tasks — Infraestrutura e Deploy (AWS)

> Backlog **da execução** do deploy. O desenho, as justificativas e os números estão em
> [`infra/infraestrutura-nuvem.md`](./infraestrutura-nuvem.md) — este arquivo não os repete,
> apenas referencia (`§x.y`, `Rn`, `Parte n`). Em caso de conflito, o `CLAUDE.md` da raiz prevalece.
>
> Status: `[ ]` pendente · `[x]` concluído · `[-]` em progresso
> Prefixo das tasks: **`D-xx`** (Deploy) — não confundir com as `I-xx` de
> [`frontend/docs/tasks-integracao.md`](../frontend/docs/tasks-integracao.md), que são de integração.

---

## O que são as trilhas

O deploy do StockSense é duas coisas independentes que só se encontram no fim. Misturá-las é o que
dá a sensação de não saber por onde começar — porque cada tarefa parece depender de todas as outras.
Separadas, a ordem fica óbvia.

**Trilha `A` — a infraestrutura funciona.**
A EC2 está no ar, o Caddy serve HTTPS com certificado válido, o backend responde em `/api/*`, o
ml-service e o MySQL estão isolados na rede Docker, o banco persiste ao reiniciar e o backup roda.
Isto **não depende do frontend**. Um front em mock exercita exatamente o mesmo roteamento, o mesmo
TLS, o mesmo build e o mesmo orçamento de memória que um front integrado.

**Trilha `B` — o produto está navegável.**
As 10 telas consomem a API real em vez do mock. Essa trilha **já tem backlog próprio** e não é
duplicada aqui: é o `frontend/docs/tasks-integracao.md` (I-01…I-11). Este arquivo só a referencia
onde ela bloqueia alguma coisa.

**Por que separar.** Seis dos oito épicos abaixo são trilha `A` pura — dá para levar a infra até o
ar sem tocar uma linha do frontend. O único ponto onde `B` trava `A` é a validação ponta a ponta
(Épico D5), e validação é conferência, não construção.

**Por que não esperar a trilha B para começar a A.** Os riscos de infra são todos de descoberta
tardia: o build do Gradle estourando os 4 GB da t3.medium (§9.3), o `docker compose` sem porta
publicada derrubando o acesso, o Let's Encrypt aplicando rate limit depois de cinco tentativas
falhas, o OOM killer durante o lote do motor (§6.1). Descobrir isso em setembro custa uma tarde.
Descobrir na véspera da defesa custa a defesa.

> **Recomendação de execução:** rodar `A` até o Épico D4 com o frontend ainda em mock, validar a
> infra, e só então fechar `B` e redeployar. O redeploy do front é um `git pull` — ele é bind mount,
> não precisa nem de rebuild de imagem.

**Legenda de trilha:** `A` infra no ar · `B` produto integrado · `A+B` só fecha com as duas.

| Épico | Trilha |
|---|---|
| D0 — Ensaio local do stack de produção | `A` |
| D1 — Correções de código pré-deploy | `A` (exceto D-11, que é `B`) |
| D2 — Decisões de deploy pendentes | `A` |
| D3 — Provisionar a AWS | `A` |
| D4 — Subir a aplicação na EC2 | `A` |
| D5 — Validação ponta a ponta em produção | `A+B` |
| D6 — Operação | `A` |
| D7 — Evidência para o TCC | `A` |

---

## Estado atual (auditado em 2026-08-30)

Auditado contra o código e o `git log`, não contra a documentação.

| Item | Estado |
|---|---|
| `infra/infraestrutura-nuvem.md` | ✅ commit `eb147c6` |
| `infra/terraform/*.tf` (9 arquivos) | ✅ commit `4a479d5` — **escrito e inicializado, nunca aplicado** |
| `Caddyfile` | ✅ commit `fabf7b3` |
| `docker-compose.prod.yml` | ✅ commit `fabf7b3` |
| Correções da Parte 8 | 🔶 **4 de 8** (D-10, D-12, D-13, D-15) · 1 descartada (credencial) |
| Integração do frontend (`tasks-integracao.md`) | ❌ **0 de 11** — o app é 100% mock |
| Recursos na AWS | ❌ **nenhum existe** — nunca houve `terraform apply` |
| `ml-service/analysis/` (núcleo acadêmico da T10) | ✅ versionado na branch `analise-validacao-modelos` — **não mergeada** |
| Benchmark do motor (T-54) | ✅ executado em 2026-08-30 — `docs/benchmark-motor.md` |
| Pin `cmdstanpy==1.2.4` (T-12) | ✅ **na branch de deploy** (D-46) e **validado na imagem** no D-04 — ainda ausente na `main` |

**Escrito ≠ executado.** O Terraform tem `terraform init` rodado (o `.terraform.lock.hcl` está
versionado), mas nunca passou por `plan` nem `apply`. Nenhum dólar de crédito foi gasto até aqui.

---

## Épico D0 — Ensaio local do stack de produção `Trilha A`

> **Antes de gastar um dólar.** Todo o Épico D4 pode falhar por motivos que aparecem na sua máquina,
> de graça, em vinte minutos. Este épico é o que mais reduz risco por hora investida.

- [x] **D-01 — Escrever `docker-compose.prod.yml` e `Caddyfile`** `A`
  Compose de produção com só o Caddy publicando porta, credenciais sem default (`${VAR:?}`),
  limites de memória por container (§6.1) e rotação de log. `Caddyfile` com `SITE_ADDRESS` por env,
  rota `/api/*` → `backend:8080` e o resto → `frontend:80`.
  Commit `fabf7b3`.

- [x] **D-02 — Commitar os dois arquivos** `A`
  Commit `fabf7b3`, junto do move de `infraestrutura-nuvem.md` para `infra/`. Confirmado antes que
  o `.gitignore:4` (`*.env`) cobre o `.env` — nenhuma credencial foi versionada.
  _Depende de: D-01_

- [x] **D-03 — `.env` de ensaio local** `A`
  Feito em 2026-09-05. Arquivo **`.env.ensaio`** (não `.env`), com as cinco variáveis que o
  `docker-compose.prod.yml` exige via `${VAR:?}`: `DB_ROOT_PASSWORD`, `DB_USERNAME`, `DB_PASSWORD`,
  `JWT_SECRET` (24 bytes aleatórios) e `SITE_ADDRESS=:80`. Senhas de ensaio, descartáveis.
  Coberto pelo `.gitignore:3` (`.env.*`) — verificado com `git check-ignore`.
  ⚠️ **O nome importa.** O compose carrega `.env` do diretório do projeto automaticamente: criar o
  arquivo de ensaio com esse nome sobrescreveria o `.env` de desenvolvimento, que já existe e tem
  as três credenciais de dev. Daí `.env.ensaio` + `--env-file` explícito.

- [x] **D-04 — Subir o stack de produção na máquina local** `A`
  Feito em 2026-09-05. Os cinco containers `running`; `db`, `ml-service` e `backend` `healthy`.
  Imagens: `stocksense-backend:prod` **273 MB**, `stocksense-ml:prod` **685 MB** — bem abaixo do
  1,5–2,5 GB que o R4 temia para o ml-service (o `.dockerignore` do D-15 ajudou). O Flyway rodou as
  migrations na subida (query em `stocksense.produto` responde).
  ⚠️ **O comando do backlog não pode ser usado cru.** `docker compose -f docker-compose.prod.yml
  up -d` compartilha diretório com o compose de desenvolvimento, então herda o mesmo nome de
  projeto (`code`) e **o mesmo volume `db_data`** — o ensaio subiria em cima do banco de dev. Pior:
  o MySQL só aplica `MYSQL_USER`/`MYSQL_PASSWORD` na primeira inicialização, então as senhas de
  ensaio seriam silenciosamente ignoradas e o backend falharia a autenticação por um motivo que não
  aparece em lugar nenhum. Os `container_name` também são idênticos nos dois arquivos (nome de
  container é global no Docker, colide até com container parado), e ambos publicam a porta 80.
  **Comando correto:**
  ```
  docker compose down    # remove os containers de dev; sem -v o volume fica
  docker compose -p stocksense-prod -f docker-compose.prod.yml --env-file .env.ensaio up -d
  ```
  O `-p` dá ao ensaio volumes próprios (`stocksense-prod_db_data`, `_caddy_data`, `_caddy_config`),
  separados do `code_db_data` de desenvolvimento. Confirmado após a subida: os dois coexistem.
  Para derrubar: `docker compose -p stocksense-prod -f docker-compose.prod.yml down`.
  _Depende de: D-03_

- [x] **D-05 — Validar o isolamento (R6)** `A`
  Feito em 2026-09-05. `curl localhost:8000/health` e a porta 8080 **recusam** conexão do host, e
  `docker exec backend wget -qO- http://ml-service:8000/health` responde
  `{"status":"ok","service":"ml-service","version":"1.0.0"}`. `docker port stocksense-db` volta
  vazio: nenhum dos três serviços internos publica porta.
  ⚠️ **Falso positivo a não repetir:** a 3306 **está** aberta no host desta máquina, mas quem
  escuta é um **MySQL nativo do Windows** (`mysqld`, PID 6648), não o container. Testar a 3306 com
  `mysql -h localhost` como o backlog sugeria daria "conectou" e passaria a impressão de vazamento.
  O teste que vale é `docker port <container>` — na EC2, onde não há MySQL nativo, os dois
  coincidem.
  _Depende de: D-04_

- [x] **D-06 — Validar o roteamento do Caddy** `A`
  Feito em 2026-09-05. `GET http://localhost/` → **200**, `text/html`, `<title>StockSense</title>`.
  `POST http://localhost/api/auth/login` → **404**, e a resposta prova que veio do backend, não do
  nginx: `Content-Type: application/problem+json` (o RFC 7807 da T-04), corpo
  `{"detail":"E-mail ou senha inválidos.",...}`, headers do Spring Security e `Via: 1.1 Caddy`.
  Confirma o desenho de mesma origem do §3.4 — sem CORS.
  📌 **Observação para a trilha B:** credencial inválida devolve **404**, não 401. Funciona, mas o
  front precisa tratar 404 no login como "credencial inválida" e não como "rota não existe" — vale
  conferir contra a I-03 do `tasks-integracao.md`.
  _Depende de: D-04_

- [~] **D-07 — Medir memória contra o orçamento do §6.1** `A` `parcial: falta sob carga`
  Medido em 2026-09-05, **stack ocioso** (`docker stats --no-stream`):

  | Container | Uso | Limite | % |
  |---|---|---|---|
  | `db` | 454,5 MiB | 600 MiB | **75,8%** |
  | `ml-service` | 282,1 MiB | 1,758 GiB | 15,7% |
  | `backend` | 276,2 MiB | 1 GiB | 27,0% |
  | `frontend` | 11,3 MiB | — | — |
  | `caddy` | 10,8 MiB | — | — |

  **Total ocioso ~1,01 GiB** dos 3,9 GB orçados — folga confortável parada.
  🔶 **O `db` é o apertado:** 75,8% do limite **sem nenhuma carga**, com
  `--innodb-buffer-pool-size=256M`. Sob importação e lote, é o primeiro candidato ao OOM killer.
  Considerar subir o `mem_limit` de 600m (há folga no orçamento) ou baixar o buffer pool.
  ⚠️ **Falta a medição sob carga**, que é a que a task chama de número útil. O banco de ensaio tem
  **0 produtos** — medir o pico exige importar planilhas e rodar `POST /api/motor/recalcular`
  antes. Fica para uma sessão com dados, ou para o **D-43** na instância.
  _Depende de: D-04_

- [ ] **D-08 — Avaliar: Caddy servindo o estático, sem o container nginx** `A` `opcional`
  O Caddy tem `file_server` embutido. Trocar o proxy para `frontend:80` por `root * /srv` +
  `file_server` elimina um container, ~50 MB de RAM no orçamento apertado do §6.1 e um salto por
  requisição. O nginx de hoje é a imagem crua servindo um bind mount — não há `nginx.conf` próprio
  a preservar. Testar aqui, onde errar custa zero; decidir antes do D-30.
  _Depende de: D-06_

---

## Épico D1 — Correções de código pré-deploy `Trilha A` (exceto D-11)

> Os 8 itens da Parte 8, um por task. Referências reconferidas contra o código em 2026-08-30 —
> **nenhuma foi feita ainda.**

- [ ] **D-09 — `API_BASE_URL` relativo** `A`
  `frontend/web/js/core/config.js:1`: `'http://localhost:8080/api'` → `'/api'`. Front e API na mesma
  origem via Caddy; elimina o `localhost` e a necessidade de CORS.
  ⚠️ Coordenar com a **I-02** do `tasks-integracao.md`, que pede a URL absoluta para o dev fora do
  Docker. Solução sugerida: relativo por padrão, absoluto por override explícito.

- [x] **D-10 — `JWT_SECRET` obrigatório** `A`
  Feito em 2026-08-30. `application.yml` passa a ter `secret: ${JWT_SECRET}`, sem default: variável
  ausente agora **quebra o boot** em vez de subir calado com o segredo versionado.
  **Não era um arquivo só.** O `docker-compose.yml` de desenvolvimento não passava `JWT_SECRET` —
  dependia exatamente do default removido. Recebeu o **mesmo valor de antes**, agora explícito, com
  fallback `${JWT_SECRET:-...}`. Em dev nada muda: mesma chave, tokens existentes continuam válidos.
  Os testes não carregam contexto Spring (não há `@SpringBootTest`), então não foram afetados.
  Nota de proporção: o valor desta task **não é segurança** — quem tem o segredo também tem a
  credencial seedada, que decidimos manter (ver a nota da D-16). O ganho é operacional: erro de
  digitação no `.env` de produção falha alto em vez de silenciosamente.

- [ ] **D-11 — Inverter o default do mock** `B` ⚠️
  **A expressão `localStorage.getItem('stocksense_mock') !== 'off'` aparece 6 vezes em 3 arquivos:**
  `js/core/apiClient.js:8`, `js/components/layout.js:131,134,151`, `js/pages/login.page.js:45,50`.
  A Parte 8 aponta só a primeira — mudar só ela dessincroniza o botão flutuante do comportamento
  real (o botão mostraria "mock ligado" com a API real respondendo). Inverter as seis:
  `!== 'off'` → `=== 'on'`. **O botão permanece** — só o default muda, porque `localStorage` é por
  navegador e por dispositivo: sem inverter, a banca, o orientador e qualquer aba anônima veem
  dados falsos.
  _Trilha `B`: só faz sentido com `tasks-integracao.md` fechado — antes disso, desligar o mock
  quebra as telas._

- [x] **D-12 — Spring Actuator** `A`
  Feito em 2026-08-30. Quatro arquivos, não dois:
  `build.gradle.kts` (dependência), `application.yml` (`management.endpoints.web.exposure.include:
  health` + `show-details: never`), `SecurityConfig.kt` e `docker-compose.prod.yml` (healthcheck
  descomentado).
  ⚠️ **O `SecurityConfig` era o pulo do gato e não estava no backlog.** Com
  `anyRequest().authenticated()`, o `/actuator/health` exigiria JWT e o healthcheck do Docker
  tomaria 401 **para sempre** — o container ficaria `unhealthy` desde a subida. Foi preciso
  acrescentar `requestMatchers("/actuator/health").permitAll()`.
  Expor o health sem autenticação é seguro aqui: `show-details: never` devolve só
  `{"status":"UP"}`, e o `Caddyfile` não tem rota para `/actuator` — quem vier de fora cai no
  frontend e recebe 404. O endpoint só existe dentro da rede Docker.
  Verificado com `./gradlew build` e `./gradlew test`: ambos passando.

- [x] **D-13 — `async def predict` → `def predict`** `A`
  Feito em 2026-08-30. **A Parte 8 subestimava: não era uma linha, eram três arquivos.** A rota
  fazia `return await executar_previsao(...)`, e `executar_previsao` era `async def` — mas sem um
  único `await` no corpo, chamando direto o código bloqueante de Holt-Winters, Prophet e estoque.
  Async de fachada: travava o event loop e derrubava o `GET /health` durante o lote (R2).
  Alterados: `predict_router.py` (assinatura + `await`), `prediction_service.py:28`
  (`async def executar_previsao` → `def`) e `test_predict_router.py` (8 mocks de `AsyncMock` para
  `MagicMock`, já que a função deixou de ser corrotina). **66 testes passando.**
  Ainda pendente: apertar `interval`/`retries` do healthcheck do ml-service no compose, hoje
  generosos por causa deste problema — fazer depois da medição do D-07.

- [ ] **D-14 — `--workers 2` no Dockerfile do ml-service** `A` `aguardando medicao`
  Hoje a flag está no `command:` do `docker-compose.prod.yml` — funciona, mas o lugar dela é o
  `ml-service/Dockerfile`. Ao mover, remover o `command:` do compose.
  ⚠️ **Duas ressalvas levantadas em 2026-08-30, antes de mover:**
  (1) **Não acelera o lote como ele é hoje.** O `MotorController` itera os produtos em sequência —
  existe uma chamada `/predict` por vez. Dois workers só ajudam com chamadas concorrentes, que não
  existem. O ganho real é o `/health` ser servido pelo outro worker e o headroom futuro.
  (2) **Pode não caber na memória.** Cada worker é um processo separado carregando Prophet,
  CmdStan, pandas, statsmodels e scikit-learn — o §6.1 reserva 1,8 GB para o ml-service inteiro.
  **Decidir o número de workers só depois do D-07.** O compose já está com 2, então o ensaio local
  mede exatamente a configuração em dúvida.

- [x] **D-15 — `.dockerignore` do ml-service** `A`
  Feito em 2026-08-30: acrescentados `analysis/`, `docs/` e `.ipynb_checkpoints/`. Sem isso, os
  notebooks, as 14 figuras e os PDFs entrariam numa imagem que já é de 1,5–2,5 GB (R4).
  **Correção de uma nota anterior deste arquivo:** eu havia registrado que `ml-service/analysis/`
  estava fora do git e "existia só nesta máquina". **Errado** — ele está versionado e no remoto, na
  branch `analise-validacao-modelos`. O que aparecia como untracked no working tree eram só sobras
  de `.ipynb_checkpoints/`, agora cobertas pelo `.gitignore` da raiz.

- [x] **D-46 — Levar o pin `cmdstanpy==1.2.4` para a branch de deploy** `A`
  Feito em 2026-09-05. Uma linha em `ml-service/requirements.txt`, logo abaixo do
  `prophet==1.1.6`, idêntica à da `analise-validacao-modelos` — mesma versão, mesmo comentário.
  **Só o pin veio; a branch continua sem merge.** A task previa resolver isto "junto com a decisão
  de mergear a `analise-validacao-modelos`". A decisão segue aberta, mas separá-las é o certo: a
  branch carrega notebook e PDFs que não têm por que entrar na branch de deploy (e que o
  `.dockerignore` do D-15 já exclui da imagem). O pin é o único item de lá que a imagem de
  produção precisa.
  Confirmado que o venv local tem `cmdstanpy 1.2.4` instalado — o pin descreve o ambiente em que o
  benchmark do D-41 produziu números válidos, não um palpite.
  ✅ **Validado no D-04 (2026-09-05).** Dentro da imagem `stocksense-ml:prod`: `pip show cmdstanpy`
  → **1.2.4**, e um `Prophet().fit()` com 60 pontos treinou e previu 67 usando
  `CmdStanPyBackend` — sem fallback silencioso. A comparação de modelos da T10 é válida na imagem
  que vai para a nuvem.

  Contexto original (2026-08-30): o `ml-service/Dockerfile` faz `pip install -r requirements.txt`
  e, sem o pin, o pip resolve o `cmdstanpy` livremente (provavelmente 1.3.0), que quebra o backend
  Stan do Prophet 1.1.6. **A falha é silenciosa** — o motor cai em fallback para Holt-Winters e
  continua respondendo 200. A imagem de produção rodaria sem Prophet e a comparação de modelos
  (T10, núcleo acadêmico do TCC) seria inválida sem nenhum erro visível.
  _Destrava: D-04, D-30, D-33._

> **D-16 removida em 2026-08-30.** Era "trocar a credencial seedada da `V2` por uma `V4`".
> Descartada por duas razões. (1) Migration é o instrumento errado: ela é versionada e roda igual em
> todos os ambientes, então uma `V4` com o hash novo só moveria o segredo de arquivo — e invalidar a
> credencial quebraria o `admin123` que o `tasks-integracao.md` usa em dev. (2) O risco prático num
> TCC é próximo de zero: a URL é conhecida por três pessoas, a instância fica desligada por padrão
> (§7.1) e os dados são reconstruíveis por reimportação (§7.2).
> Vira **limitação consciente**, registrada no §10.2 do `infraestrutura-nuvem.md`. Se em algum
> momento a senha precisar mudar, o caminho é um `UPDATE` no banco: o `AuthController` só tem
> `/login`, e a T9 (alterar senha) é Pós-MVP — não existe outra via.

---

## Épico D2 — Decisões de deploy pendentes `Trilha A`

> ⚠️ **Não é código.** São três decisões que travam a execução e que nenhum documento registrou
> ainda. Cada uma muda tasks do D3 e do D4.

- [ ] **D-17 — Como o código chega na EC2** `A` `BLOQUEADOR`
  O `user_data` do `compute.tf` instala Docker, compose e o swap — mas **não clona nada**. O repo é
  `github.com/tcc-stocksense/code`. Duas saídas:
  **(a) `git clone` na VM** — se o repo for privado, exige deploy key ou PAT na instância, e o build
  roda na t3.medium, onde o §9.3 avisa que pode estourar a memória.
  **(b) build local + push para ECR ou Docker Hub**, deixando a EC2 só com `docker compose pull`.
  Resolve o problema de memória junto, ao custo de um registry (o ECR não está no Terraform).
  A escolha define D-28 e D-30. **Sem ela, o deploy para.**

- [ ] **D-18 — Domínio** `A`
  DuckDNS grátis (`stocksense.duckdns.org`) ou `.com` próprio (~US$ 12/ano, melhor na defesa).
  Precisa estar **resolvendo para o Elastic IP antes** do primeiro `up` com TLS — ver D-32.

- [ ] **D-19 — Deployar com o front em mock, ou esperar a trilha B?** `A`
  A recomendação deste arquivo é **deployar antes**: valida infra cedo e o redeploy do front é um
  `git pull` (bind mount, sem rebuild). Registrar a decisão aqui de qualquer forma — ela define se
  o Épico D5 roda uma vez ou duas.

---

## Épico D3 — Provisionar a AWS `Trilha A`

- [x] **D-20 — Escrever os manifestos Terraform** `A`
  VPC + subnet pública + IGW + route table (`network.tf`), `SG-web` com 443/80 públicos e 22
  restrito ao dev, EC2 t3.medium com EBS gp3 30 GB criptografado e Elastic IP (`compute.tf`),
  bucket S3 com lifecycle e IAM role de `s3:PutObject` mínimo (`backup.tf`), outputs úteis
  (`outputs.tf`). Key pair gerado pelo próprio Terraform. `user_data` automatizando Docker, swap de
  2 GB e AWS CLI.
  Commit `4a479d5`. **`terraform init` rodado; `plan` e `apply`, nunca.**

- [ ] **D-21 — `terraform.tfvars`** `A`
  Copiar do `.example` e preencher `dev_ip` com `curl -s https://checkip.amazonaws.com` + `/32`.
  A `validation` do `variables.tf` rejeita CIDR malformado. O arquivo é gitignorado.
  ⚠️ IP residencial muda. Se o SSH parar de conectar depois de um tempo, é isto — reaplicar com o
  IP novo.

- [ ] **D-22 — `terraform plan` revisado** `A`
  Ler o plano inteiro antes de aplicar. Conferir explicitamente: **nenhum `aws_nat_gateway`**
  (~US$ 32/mês, um terço do crédito — §4.2), um único Elastic IP, e o `SG-web` sem regra para
  8080/8000/3306.
  _Depende de: D-21_

- [ ] **D-23 — Alarme de orçamento** `A`
  **Recurso que falta no Terraform.** São US$ 100 de crédito e nada avisa se a instância ficar
  ligada esquecida. Adicionar `aws_budgets_budget` com notificação por e-mail em ~50% e ~80%.
  Escrever antes do `apply` para entrar na mesma execução.
  _Depende de: D-22_

- [ ] **D-24 — `terraform apply`** `A`
  Guardar os outputs: `ip_publico`, `instance_id`, `bucket_backup`, `comando_ssh`. O
  `bucket_backup` tem sufixo aleatório (`random_id`) — o script do D-36 precisa desse nome.
  _Depende de: D-22, D-23_

- [ ] **D-25 — Proteger o `.tfstate` e o `.pem`** `A` ⚠️
  O state fica **local** e guarda a **chave SSH privada em texto claro**; o
  `stocksense-key.pem` é gravado ao lado. Ambos são gitignorados — e é justamente por isso que
  perder a pasta significa perder o controle da infra (sem SSH, sem `destroy` limpo). Fazer cópia
  fora do repositório, num lugar que não seja só este notebook. Backend remoto em S3 é o caminho
  "certo", mas é overkill para um projeto de uma pessoa.
  _Depende de: D-24_

- [ ] **D-26 — Apontar o DNS** `A`
  Cadastrar o subdomínio escolhido no D-18 apontando para o `ip_publico`. Confirmar com
  `nslookup` **antes** de subir o Caddy com TLS.
  _Depende de: D-18, D-24_

- [ ] **D-27 — Confirmar o bootstrap** `A`
  Entrar por SSH (~3 min após o `apply`) e verificar:
  `ls /var/log/stocksense-bootstrap-done`, `free -h` (2 GB de swap ativos), `docker --version`,
  `docker compose version`, `aws --version`. Se o arquivo-sentinela não existir, o `user_data`
  falhou — ler `/var/log/cloud-init-output.log`.
  _Depende de: D-24_

---

## Épico D4 — Subir a aplicação na EC2 `Trilha A`

- [ ] **D-28 — Levar o código/imagens para a instância** `A`
  Executar o que o D-17 decidiu.
  _Depende de: D-17, D-27_

- [ ] **D-29 — `.env` de produção na VM** `A`
  As quatro variáveis com **valores novos e fortes** (`JWT_SECRET` com 32+ bytes aleatórios),
  `SITE_ADDRESS` com o domínio do D-18, `chmod 600`. **Nunca versionado, nunca reaproveitado do
  ensaio local.**
  _Depende de: D-26, D-28_

- [ ] **D-30 — Build, uma imagem por vez** `A`
  Se o D-17 escolheu build na VM: `build ml-service`, **depois** `build backend` — em paralelo
  estoura os 4 GB (§9.3). Se escolheu registry: `docker compose pull`.
  _Depende de: D-28_

- [ ] **D-31 — `up -d` e healthchecks internos** `A`
  Subir, conferir `ps` (todos `running`, `db` e `ml-service` `healthy`) e bater nos healthchecks
  por dentro (§9.6). O `/actuator/health` do backend só existe depois do D-12.
  _Depende de: D-29, D-30_

- [ ] **D-32 — Certificado TLS emitido** `A`
  `https://<domínio>` com cadeado válido, e `http://` redirecionando sozinho.
  ⚠️ **Rate limit do Let's Encrypt: 5 falhas por hora por hostname.** Se o DNS não estava propagado
  no primeiro `up`, o ACME falha; repetir às cegas queima a cota e você fica uma hora sem conseguir
  emitir. Conferir o DNS antes, e ler `docker compose logs caddy` ao primeiro erro.
  Confirmar também que o volume `caddy_data` persiste — sem ele, cada `up` pede certificado novo.
  _Depende de: D-31_

---

## Épico D5 — Validação ponta a ponta em produção `Trilha A+B`

> **É aqui que as duas trilhas se encontram.** Antes do `tasks-integracao.md` fechar, só o D-33 roda.

- [ ] **D-33 — Fumaça pela API** `A`
  Rodar a coleção `docs/postman/StockSense_E2E.postman_collection.json` contra a URL de produção:
  login → `POST /api/importacao/produtos` → `/vendas` → `POST /api/motor/recalcular` → conferir
  dashboard, alertas, curva ABC e métricas. **Valida a trilha A inteira sem depender do frontend.**
  _Depende de: D-32_

- [ ] **D-34 — Fluxo completo pela interface** `A+B`
  O mesmo roteiro pelo navegador, com o mock desligado por padrão (D-11). Critério: sem erro no
  console, e os dados batendo com os do D-33.
  Testar **também antes de rodar o motor**, para exercitar os estados `null` — o
  `tasks-integracao.md` avisa que todo campo calculado vem `null` até o primeiro recálculo.
  _Depende de: D-33, D-11, `tasks-integracao.md` I-11_

- [ ] **D-35 — Cronometrar o lote real** `A`
  Medir `POST /api/motor/recalcular` com o catálogo completo na t3.medium. É o número que confirma
  (ou derruba) a estimativa de 5–25 min do R1, e ele vai para a metodologia do TCC.
  _Depende de: D-33_

---

## Épico D6 — Operação `Trilha A`

- [ ] **D-36 — `infra/scripts/backup.sh` versionado** `A`
  Hoje o script existe **só como bloco de código no §9.7**. Virar arquivo de verdade, recebendo o
  nome do bucket por variável de ambiente (ele tem sufixo aleatório — output do D-24) e a senha do
  root por `.env`. `mysqldump` → `gzip` → `aws s3 cp`. A instance profile autentica: **nenhuma
  access key no disco.**
  _Depende de: D-24_

- [ ] **D-37 — Agendar o backup** `A`
  Instalar em `/etc/cron.daily/`. Confirmar que o objeto aparece no S3 no dia seguinte.
  _Depende de: D-36, D-31_

- [ ] **D-38 — Testar a restauração** `A`
  Backup não testado não é backup. Baixar um dump e restaurar num MySQL descartável, conferindo a
  contagem de linhas de `produto` e `venda`.
  _Depende de: D-37_

- [ ] **D-39 — Runbook de ligar/desligar** `A`
  Documentar o §9.8 com o `instance_id` real: o que para de ser cobrado (CPU/RAM) e o que continua
  (~US$ 6/mês de EBS + IPv4). Confirmar na prática que os containers voltam sozinhos pelo
  `restart: unless-stopped` e que **o banco não perde dados** — é a demonstração do §7.2.
  _Depende de: D-31_

- [ ] **D-40 — Snapshot do EBS antes da defesa** `A`
  Restaura a máquina inteira, não só o banco. Fazer com o sistema já carregado e validado.
  _Depende de: D-34_

---

## Épico D7 — Evidência para o TCC `Trilha A`

> A infraestrutura vira capítulo. Estes números são material de defesa, não sobra de engenharia.

- [x] **D-41 — Rodar o benchmark do motor (T-54)** `A`
  Executado em 2026-08-30 na máquina de desenvolvimento. Relatório em `docs/benchmark-motor.md`.
  **0,42–0,53 s/produto**, escala linear, 0 falhas, nenhuma chamada acima de 1,1 s, Prophet ativo em
  500/500 chamadas. Projeção de **~2,8 min** para 312 SKUs — contra os **5 a 25 min** que o R1
  estimava. O `read-timeout` de 30 s do Feign sai da lista de riscos.
  Consequências: o §6.2 confirma a **t3.medium** (sem necessidade de instância maior) e o Épico 7
  deixa de ser bloqueador — ver a conclusão do relatório.
  ⚠️ Medido em desktop de 12 CPUs, fora do Docker. **Não é o número da t3.medium** — quem fecha
  isso é o D-35.

- [ ] **D-42 — Monitorar `CPUCreditBalance` no primeiro lote** `A`
  A t3 é burstable. Se o saldo zerar durante o lote, a instância é limitada e o recálculo se arrasta
  (§6.2). Gráfico do CloudWatch durante o D-35.
  _Depende de: D-35_

- [ ] **D-43 — Memória real sob carga** `A`
  `docker stats` e `free -h` durante o lote, na instância. Confronto com o orçamento de 3,9 GB do
  §6.1 e verificação de quanto swap foi realmente tocado.
  _Depende de: D-35_

- [ ] **D-44 — Custo real vs. estimado** `A`
  Cost Explorer depois de algumas semanas, contra a tabela do §7.1. Fecha o argumento de por que
  ALB, ECS Fargate, NAT Gateway e RDS ficaram de fora.
  _Depende de: D-24_

- [ ] **D-45 — Capturas e diagramas finais** `A`
  Console da AWS (VPC, SG, EC2, S3), cadeado do HTTPS, `docker compose ps` na instância, sistema
  com dados reais. Confrontar os diagramas do §3.2 e §3.3 com o que o Terraform de fato criou.
  _Depende de: D-34_

---

## Dependências cruzadas

| Este arquivo | Depende de | Onde |
|---|---|---|
| D-11 (mock off) | I-01 … I-11 completos | `frontend/docs/tasks-integracao.md` |
| D-34 (fluxo pela UI) | I-11 (fumaça E2E no navegador) | `frontend/docs/tasks-integracao.md` |
| D-09 (`API_BASE_URL`) | I-02 (base URL) — **decidir juntas** | `frontend/docs/tasks-integracao.md` |
| D-12 (Actuator) | `backend/build.gradle.kts` | `backend/tasks.md` |

---

## Riscos e limitações

Não duplicados aqui — estão em `infra/infraestrutura-nuvem.md` §10.1 (riscos priorizados, com
severidade e mitigação) e §10.2 (limitações conscientes: instância única, banco em container,
backend em 1 réplica por causa do R5, sem CI/CD, motor síncrono). A §10.2 é material de defesa:
são escolhas justificadas, e devem ser apresentadas assim.

---

*Atualizar o status (`[ ]` → `[x]`) conforme as tarefas forem concluídas, com uma nota quando a
execução divergir do planejado — a convenção do `backend/tasks.md`. Decisões novas de arquitetura
vão para `infra/infraestrutura-nuvem.md`; o que muda invariante vai para o `CLAUDE.md` da raiz.*
