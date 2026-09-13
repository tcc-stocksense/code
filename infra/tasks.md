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

## Estado atual (auditado em 2026-09-13)

Auditado contra o código, o `git log` e os recursos que existem de fato na AWS.
**O sistema está no ar** desde 2026-09-13 em `http://107.20.236.251`.

| Item | Estado |
|---|---|
| `infra/infraestrutura-nuvem.md` | ✅ commit `eb147c6` |
| `infra/terraform/*.tf` | ✅ adaptado ao Learner Lab e **aplicado** — 15 de 16 recursos (ver D-24) |
| `Caddyfile` | ✅ commit `fabf7b3` |
| `docker-compose.prod.yml` | ✅ commit `fabf7b3` |
| Scripts de deploy (`infra/scripts/`) | ✅ 01 a 05 + `backup.sh` + `medir-memoria.sh` — **todos executados com sucesso**, exceto o `backup.sh` |
| Correções da Parte 8 | ✅ **6 de 8** (D-09, D-10, D-11, D-12, D-13, D-15) · D-14 destravado, ver nota · 1 descartada (D-16) |
| Integração do frontend (`tasks-integracao.md`) | ✅ **10 de 11** — falta a I-11, agora executável contra a URL de produção |
| **Recursos na AWS** | ✅ **EC2 `i-01fb1975491b85fb1` (t3.medium) rodando**, EIP `107.20.236.251`, VPC, SG, bucket S3 |
| **Aplicação em produção** | ✅ 5 containers `healthy`; fumaça completa passou (D-33) |
| `ml-service/analysis/` (núcleo acadêmico da T10) | ✅ versionado na branch `analise-validacao-modelos` — **não mergeada** |
| Benchmark do motor (T-54) | ✅ 2026-08-30 — `docs/benchmark-motor.md`; confirmado na t3.medium no D-35 |
| Pin `cmdstanpy==1.2.4` (T-12) | ✅ **validado na EC2** — Prophet MAPE 14,18% × HW 55,74% no D-33. Ainda ausente na `main` |

**O que falta para o TCC não é mais infraestrutura.** O caminho crítico do deploy fechou:
D-21 → D-33 concluídos. O que resta são HTTPS (D-18/D-26/D-32, adiados de propósito), o backup
(D-36…D-39, bloqueado pela SCP do lab) e os números de evidência (D-34, D-42, D-44, D-45), mais
as medições que exigem catálogo real de ~312 SKUs (D-07, D-35, D-43).

### Restrições do AWS Academy Learner Lab (atualizado em 2026-09-13)

A conta é **Learner Lab**, não uma conta AWS comum — o que o §7 deste projeto assumia. **Cinco**
consequências, a última descoberta durante o apply:

| Restrição | Efeito |
|---|---|
| `iam:CreateRole` negado | O `backup.tf` **não cria role/policy/instance profile**. Usa a `LabRole` pronta (`var.instance_profile_name = "LabInstanceProfile"`, confirmado no console). Perde-se o privilégio mínimo de `s3:PutObject` — registrar no §10.2 |
| `budgets:*` negado | **D-23 não aplicável.** O controle de gasto é o painel do próprio lab |
| `s3:GetBucketObjectLockConfiguration` negado por SCP | **Descoberto no apply (D-24).** Aborta a criação do bucket depois de criá-lo, deixando de fora bloqueio público, criptografia e **lifecycle**. Faz qualquer apply futuro falhar no mesmo ponto. Bloqueia o D-37 |
| Credenciais temporárias | Expiram em ~3–4h e exigem `AWS_SESSION_TOKEN`. Recolar em `infra/lab-credentials.env` a cada sessão |
| Sessão do lab encerra | O lab **para as instâncias** ao fim da sessão. O EIP e o EBS persistem; os containers voltam pelo `restart: unless-stopped`. "No ar 24/7" não existe neste ambiente |

✅ **`t3.medium` É permitida** — confirmado no apply de 2026-09-13. O plano B do D-08 (eliminar o
container nginx para caber numa `t3.small`) **não foi necessário** e volta a ser opcional.

⚠️ **Credencial seedada exposta.** Com o sistema publicado, o `admin@stocksense.local` / `admin123`
da migration `V2` está alcançável pela internet, e o hash está num repositório **público**. O D-16
descartou trocá-la assumindo que "a URL é conhecida por três pessoas e a instância fica desligada
por padrão" — a primeira premissa caiu. Mitigação: manter a instância desligada fora das
demonstrações (§7.1, que também economiza crédito) ou trocar a senha por `UPDATE` no banco.
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
  📊 **Segunda medição em 2026-09-12**, stack de produção local com as imagens novas,
  durante importação + lote do motor (amostragem a cada 3s via
  [`medir-memoria.sh`](../scripts/medir-memoria.sh), 30 amostras):

  | Container | Pico | Média | Limite | % do limite |
  |---|---|---|---|---|
  | `db` | 407,5 MiB | 407,2 | 600 MiB | **67,9%** |
  | `backend` | 337,6 MiB | 295,2 | 1 GiB | 33,0% |
  | `ml-service` | 269,8 MiB | 262,8 | 1,758 GiB | 15,0% |
  | `frontend` | 10,5 MiB | 10,4 | — | — |
  | `caddy` | 11,5 MiB | 10,8 | — | — |

  **Pico somado: 1,01 GiB** dos 3,9 GB orçados. O `db` segue o mais apertado, mas em 67,9%
  contra os 75,8% da primeira medição.
  ⚠️ **Isto ainda NÃO é a medição sob carga que a task pede, e a task continua `[~]`.** O
  catálogo sintético tem **10 produtos** (`PRODUTOS_META` no `generate_synthetic_data.py` é
  fixo), então o lote terminou em 4 s e o pico ficou igual ao ocioso. Carga real exige um
  catálogo de ~312 SKUs — trabalho no gerador do ml-service, não na infra. Quem fecha de
  verdade é o **D-43**, na instância, com dados do estabelecimento.

  ✅ **Mas rendeu um número novo e útil:** **0,40 s/produto** (4 s / 10 produtos) medido
  **dentro do container de produção**, numa VM Docker de 3,95 GB — praticamente o teto da
  t3.medium. O D-41 mediu 0,42–0,53 s/produto **fora do Docker**, em desktop de 12 CPUs, e
  avisava explicitamente que não era o número da t3.medium. Agora há evidência de que o
  contêiner não degrada o tempo por produto, o que reforça a projeção de ~2,8 min para 312
  SKUs em vez dos 5–25 min do R1.
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

## Épico D1 — Correções de código pré-deploy `Trilha A`

> Os 8 itens da Parte 8, um por task. Referências reconferidas contra o código em 2026-08-30 —
> **nenhuma foi feita ainda.**

- [x] **D-09 — `API_BASE_URL` relativo** `A`
  **Feito em 2026-09-12 — e não do jeito que esta task previa.** A solução sugerida aqui
  ("relativo por padrão, absoluto por override") resolve o sintoma mantendo a causa: dev e
  produção com topologias de origem diferentes, obrigando o front a saber onde está.
  O que foi feito: **o nginx de desenvolvimento ganhou o proxy que o Caddy já tinha**
  ([`frontend/nginx-dev.conf`](../../frontend/nginx-dev.conf), montado no
  `docker-compose.yml`). Com os dois ambientes na mesma origem, `API_BASE_URL` é `'/api'`
  puro, sem detecção de ambiente — e o bean de CORS que veio da integração passa a ser
  redundante (inofensivo) também em dev.
  Dois defaults do nginx que quebrariam o que o Caddy não quebra, e foram corrigidos no
  conf: `client_max_body_size` (1m default → 413 no upload da T3, que o backend aceita até
  5MB) e `proxy_read_timeout` (60s default → cortaria o lote do motor no meio; R1).
  Escape hatch para quem serve o front fora do Docker: `localStorage` →
  `stocksense_api_base`, documentado no próprio `config.js`.
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

- [x] **D-11 — Inverter o default do mock** `B`
  ✅ **Já estava feito quando esta task foi reavaliada (2026-09-12).** O commit de
  integração `3b5f60d` consolidou as 6 ocorrências em **uma única função** em
  `core/config.js`: `mockAtivo()` devolve `localStorage.getItem('stocksense_mock') === 'on'`.
  Não existe mais nenhum `!== 'off'` solto — `layout.js`, `apiClient.js` e
  `sugestao-compra.page.js` todos importam de `config.js`, então o botão flutuante e o
  comportamento real não podem dessincronizar, que era o risco apontado abaixo.
  Conferido também que a T8 (Pós-MVP, sem endpoint no backend) com mock desligado mostra
  um *empty state* honesto em vez de erro de console — o critério do D-34 se mantém.
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

- [x] **D-17 — Como o código chega na EC2** `A` `opção (c)`
  ✅ **Decidido em 2026-09-12: opção (c).** Build local, `docker save` → SSH →
  `docker load`; arquivos de bind mount por `git clone`. Implementado em
  [`01-empacotar-imagens.sh`](../scripts/01-empacotar-imagens.sh) e
  [`03-enviar.sh`](../scripts/03-enviar.sh).
  **A pendência de fato caiu:** `github.com/tcc-stocksense/code` é **público** (verificado
  por `api.github.com/repos/...` → HTTP 200 sem autenticação). O `git clone` do eixo (2)
  não precisa de deploy key, e o redeploy do front segue sendo `git pull`.
  **Recomendação registrada em 2026-09-06, aguardando o seu aval.** Passo a passo completo em
  **[`infra/docs/deploy-runbook.md`](docs/deploy-runbook.md)**, que também resume as alternativas.

  O backlog tratava como uma decisão o que são **duas**: (1) onde as imagens são construídas — onde
  mora o risco do §9.3 — e (2) como os arquivos de config e o front chegam à VM, que é inevitável
  nas três opções por causa dos bind mounts do `Caddyfile` e do `frontend/web`.

  **Recomendada: opção (c) — `docker save` → SSH → `docker load`,** que não estava no backlog.
  Build na máquina local, imagens prontas para a instância; os arquivos por `git clone`, mantendo o
  redeploy do front como `git pull`. **A t3.medium nunca compila nada**, então o risco do §9.3
  deixa de existir.
  Viabilizada por uma medição do D-04: as imagens ficaram em **273 MB + 685 MB (385 MB comprimidos,
  medido)**, contra os 1,5–2,5 GB que o R4 projetava para o ml-service — o que tornaria a
  transferência impraticável. O compose já suporta sem alteração: declara `image:` junto de `build:`.
  Vantagem decisiva no contexto: **todos os comandos são disparados da máquina local** por SSH, então
  diagnosticar falha não exige trabalhar dentro da instância.
  Assumido: sem histórico central de imagens — rollback por tag local + o `.tar.gz` guardado.

  **(a) `git clone` + build na VM** — um comando só, mas concentra na instância justamente o passo
  que pode falhar (§9.3: Gradle estourando os 4 GB), e depurar OOM por SSH é caro.
  **(b) registry (ECR/Docker Hub)** — tecnicamente a mais correta, com rollback central; mas o ECR
  não está no Terraform, exige autenticação na instância e não resolve o eixo (2). Peças demais
  para uma instância única.

  ⚠️ **Pendência de fato:** não foi possível confirmar se `github.com/tcc-stocksense/code` é
  privado (o `gh` não está instalado na máquina). Se for, o `git clone` do eixo (2) exige deploy
  key — ou troca-se por `scp`, ao custo de perder o `git pull` no redeploy do front.
  A escolha define D-28 e D-30.

- [~] **D-18 — Domínio** `A` `pós-primeiro-deploy`
  🔁 **Reordenado em 2026-09-12: sai do caminho crítico do primeiro deploy.** Sobe-se em
  **HTTP puro no IP** (`SITE_ADDRESS=:80`, o modo do `Caddyfile:18`), e o domínio vira um
  passo posterior de 5 minutos. Motivo: o Let's Encrypt **não emite certificado para
  endereço IP** (§5), então juntar TLS à primeira subida traz dois riscos que nada têm a
  ver com a infra funcionar — propagação de DNS e o rate limit de 5 falhas/hora do ACME,
  que trava a emissão por uma hora se o DNS não estava pronto.
  Com o stack comprovadamente no ar, `04-subir.sh stocksense.duckdns.org` troca o
  `SITE_ADDRESS` e reinicia o Caddy. **Decisão pendente apenas de quando**, não de qual:
  DuckDNS grátis para validar, `.com` próprio se quiser na defesa.
  ⚠️ **Antes da defesa isto precisa existir.** Sem HTTPS o JWT trafega em claro (a lacuna
  que o §1.7 aponta), o navegador mostra "Não seguro" e o D-45 pede "cadeado do HTTPS"
  nas capturas. HTTP no IP é estado de trânsito, não de entrega.
  DuckDNS grátis (`stocksense.duckdns.org`) ou `.com` próprio (~US$ 12/ano, melhor na defesa).
  Precisa estar **resolvendo para o Elastic IP antes** do primeiro `up` com TLS — ver D-32.

- [x] **D-19 — Deployar com o front em mock, ou esperar a trilha B?** `A`
  ✅ **Resolvido por fato consumado em 2026-09-12: a trilha B fechou antes.** A pergunta
  pressupunha front em mock; a integração foi mergeada na `main` (PR #10) com **10 das 11
  tasks** do `tasks-integracao.md` concluídas — falta só a I-11, que é o próprio teste de
  fumaça no navegador. Deploya-se com o front **integrado**, e o Épico D5 roda uma vez.
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

- [x] **D-21 — `terraform.tfvars`** `A`
  ✅ **Feito em 2026-09-13**, gerado pelo `02-provisionar.sh`. `dev_ip` resolvido por
  `checkip.amazonaws.com` e `instance_profile_name = "LabInstanceProfile"`, confirmado no
  console (IAM → Roles → LabRole → "Instance profile ARNs").
  📌 **Automatizado em 2026-09-12** no [`02-provisionar.sh`](../scripts/02-provisionar.sh):
  ele resolve o `dev_ip` por `curl checkip.amazonaws.com` a cada execução (o IP
  residencial muda) e preserva o resto do arquivo. Acrescenta `instance_profile_name`,
  que passou a existir por causa do Learner Lab. Ainda `[ ]` porque só roda amanhã.
  Copiar do `.example` e preencher `dev_ip` com `curl -s https://checkip.amazonaws.com` + `/32`.
  A `validation` do `variables.tf` rejeita CIDR malformado. O arquivo é gitignorado.
  ⚠️ IP residencial muda. Se o SSH parar de conectar depois de um tempo, é isto — reaplicar com o
  IP novo.

- [x] **D-22 — `terraform plan` revisado** `A`
  ✅ **Feito em 2026-09-13.** 16 recursos planejados; as quatro conferências passaram:
  nenhum NAT Gateway, exatamente 1 Elastic IP, SG sem 8080/8000/3306 e nenhuma role IAM
  sendo criada. `instance_type = "t3.medium"` confirmado no plano.
  Ler o plano inteiro antes de aplicar. Conferir explicitamente: **nenhum `aws_nat_gateway`**
  (~US$ 32/mês, um terço do crédito — §4.2), um único Elastic IP, e o `SG-web` sem regra para
  8080/8000/3306.
  _Depende de: D-21_

- [x] **D-23 — Alarme de orçamento** `A` `não aplicável no Learner Lab`
  ⛔ **Não aplicável no AWS Academy Learner Lab (decidido em 2026-09-12).** A política
  do lab nega `budgets:*`: incluir o recurso garantiria apply falho. O controle de gasto
  passa a ser o do próprio lab — ele mostra o crédito consumido e encerra a sessão,
  parando as instâncias. Registrar como limitação do ambiente no §10.2, não como lacuna
  do projeto. Se a conta mudar para uma AWS normal, reabrir esta task.
  **Recurso que falta no Terraform.** São US$ 100 de crédito e nada avisa se a instância ficar
  ligada esquecida. Adicionar `aws_budgets_budget` com notificação por e-mail em ~50% e ~80%.
  Escrever antes do `apply` para entrar na mesma execução.
  _Depende de: D-22_

- [~] **D-24 — `terraform apply`** `A` `15 de 16 — S3 bloqueado pela SCP`
  🔶 **Aplicado em 2026-09-13, com uma falha parcial.** 15 dos 16 recursos criados:

  | Recurso | Id |
  |---|---|
  | EC2 `t3.medium` | `i-01fb1975491b85fb1` |
  | Elastic IP | `107.20.236.251` |
  | VPC | `vpc-028883f4797082259` |
  | Security group | `sg-0d1a8c54d9a4d292d` |
  | Bucket S3 | `stocksense-backup-6a9ff8eb` |

  ✅ **`t3.medium` é permitida no Learner Lab** — era a maior incógnita do backlog, e o
  plano B do D-08 não precisou ser acionado.

  ⛔ **QUARTA restrição do Learner Lab, descoberta aqui.** O apply abortou em
  `aws_s3_bucket.backup`: uma *service control policy* da organização
  (`p-gi77lu0b`) nega `s3:GetBucketObjectLockConfiguration`, que o provider AWS lê
  automaticamente logo após criar o bucket. O bucket **foi criado e está no state**, mas os
  três recursos seguintes não chegaram a ser aplicados:
  `aws_s3_bucket_public_access_block`, `aws_s3_bucket_server_side_encryption_configuration`
  e `aws_s3_bucket_lifecycle_configuration`.
  Impacto: baixo hoje — a AWS aplica bloqueio de acesso público e SSE-S3 por padrão em
  buckets novos desde 2023. O que se perde de fato é o **lifecycle de 30 dias**, então
  dumps antigos não expiram sozinhos. Bloqueia o D-37 até ser resolvido.
  ✅ **RESOLVIDO em 2026-09-13 — e o diagnóstico acima estava incompleto.** Não eram os três
  recursos filhos: o problema é o próprio **`aws_s3_bucket`**. O provider chama
  `GetObjectLockConfiguration` ao **ler** o recurso, no create e em todo refresh posterior —
  então a partir do apply que abortou, até `terraform plan` passou a falhar, porque o
  refresh do bucket já existente batia na mesma API negada. Confirmado rodando o plan.
  Não há contorno: o provider não expõe flag para pular essa leitura, e o erro é de
  autorização, não de configuração.
  **Solução:** o S3 saiu do Terraform por completo. O `backup.tf` ficou só com a explicação,
  `aws_s3_bucket.backup` e `random_id.bucket` foram removidos do state com
  `terraform state rm` (o bucket segue existindo na AWS, sem gerência), e o output
  `bucket_backup` deixou de existir. Quem cria o bucket agora é o `backup.sh`, na primeira
  execução, com nome derivado do id da conta — determinístico e sem depender de state.
  `terraform plan` volta a rodar limpo, sem alteração de infraestrutura.
  Perde-se o **lifecycle de 30 dias**; bloqueio público e SSE-S3 continuam valendo por
  padrão da AWS. Registrar no §10.2.
  ⚠️ Ficou órfão o bucket `stocksense-backup-6a9ff8eb`, vazio e fora do Terraform.
  Guardar os outputs: `ip_publico`, `instance_id`, `bucket_backup`, `comando_ssh`. O
  `bucket_backup` tem sufixo aleatório (`random_id`) — o script do D-36 precisa desse nome.
  _Depende de: D-22, D-23_

- [x] **D-25 — Proteger o `.tfstate` e o `.pem`** `A` ⚠️
  ✅ **Feito em 2026-09-13.** Cópia em `tcc-stocksense/segredos-infra/` — **fora do
  repositório**, com `terraform.tfstate`, `stocksense-key.pem`, `outputs.env` e um
  `LEIA-ME.txt` que registra os ids dos recursos (para achar tudo no console caso o state
  se perca mesmo assim).
  **Por que fora e não em `infra/`:** os dois são gitignorados, e é justamente isso que os
  torna vulneráveis — `git clean -xdf` apaga arquivos ignorados e levaria original e cópia
  juntos. Falta ainda uma cópia fora desta máquina (Drive/pendrive), que é do usuário.
  O state fica **local** e guarda a **chave SSH privada em texto claro**; o
  `stocksense-key.pem` é gravado ao lado. Ambos são gitignorados — e é justamente por isso que
  perder a pasta significa perder o controle da infra (sem SSH, sem `destroy` limpo). Fazer cópia
  fora do repositório, num lugar que não seja só este notebook. Backend remoto em S3 é o caminho
  "certo", mas é overkill para um projeto de uma pessoa.
  _Depende de: D-24_

- [~] **D-26 — Apontar o DNS** `A` `adiada com a D-18`
  ⏸️ **Adiada junto com o D-18 (2026-09-13).** O sistema subiu em HTTP puro no Elastic IP
  `107.20.236.251`, então não há DNS a apontar ainda. Quando houver nome, é aqui que ele
  aponta — e o `nslookup` tem de confirmar **antes** do D-32, por causa do rate limit do ACME.
  Cadastrar o subdomínio escolhido no D-18 apontando para o `ip_publico`. Confirmar com
  `nslookup` **antes** de subir o Caddy com TLS.
  _Depende de: D-18, D-24_

- [x] **D-27 — Confirmar o bootstrap** `A`
  ✅ **Feito em 2026-09-13**, dentro do `03-enviar.sh`. Sentinela
  `/var/log/stocksense-bootstrap-done` presente; Docker **29.1.3** e compose **2.40.3**
  (bem mais novos que os 24.0.7 da máquina de desenvolvimento, sem consequência prática);
  **swap de 2,0 GiB ativo**, conforme o §6.1 exige.
  Entrar por SSH (~3 min após o `apply`) e verificar:
  `ls /var/log/stocksense-bootstrap-done`, `free -h` (2 GB de swap ativos), `docker --version`,
  `docker compose version`, `aws --version`. Se o arquivo-sentinela não existir, o `user_data`
  falhou — ler `/var/log/cloud-init-output.log`.
  _Depende de: D-24_

---

## Épico D4 — Subir a aplicação na EC2 `Trilha A`
- [x] **D-28 — Levar o código/imagens para a instância** `A`
  ✅ **Feito em 2026-09-13** pelo `03-enviar.sh`, executando a opção (c) do D-17. Eixo (2):
  `git clone` da branch na VM, commit `3bc38ee` — o mesmo da máquina local, então o
  `Caddyfile`, o `docker-compose.prod.yml` e o `frontend/web` montados são exatamente os
  testados no ensaio do D-04. Eixo (1): 350 MB transferidos e `docker load` sem erro.
  Executar o que o D-17 decidiu. Se confirmada a opção (c): **passos 2, 3 e 5** do
  [`docs/deploy-runbook.md`](docs/deploy-runbook.md) — empacotar (`docker save | gzip`), `git clone`
  na VM para os arquivos de bind mount, e `docker load` via SSH.
  _Depende de: D-17, D-27_
  _Depende de: D-17, D-27_

- [x] **D-29 — `.env` de produção na VM** `A`
  ✅ **Feito em 2026-09-13** pelo `04-subir.sh`. Segredos gerados na própria instância com
  `openssl rand`, nunca reaproveitados do ensaio local, `chmod 600`. O script só cria o
  arquivo se ele não existir — a lição do D-04: o MySQL aplica `MYSQL_USER`/`MYSQL_PASSWORD`
  apenas na primeira inicialização do volume, então regerar depois quebraria a autenticação
  do backend sem aparecer em log nenhum.
  As quatro variáveis com **valores novos e fortes** (`JWT_SECRET` com 32+ bytes aleatórios),
  `SITE_ADDRESS` com o domínio do D-18, `chmod 600`. **Nunca versionado, nunca reaproveitado do
  ensaio local.**
  _Depende de: D-26, D-28_

- [x] **D-30 — Build, uma imagem por vez** `A`
  ✅ **Resolvida sem existir, em 2026-09-13 — como o D-17 previu.** Com a opção (c) o build
  aconteceu na máquina local e a t3.medium recebeu imagens prontas. **A instância não
  compilou nada**, então o risco do §9.3 (Gradle estourando os 4 GB) nunca teve chance de
  se materializar. Na VM sobrou `docker load` (D-28) e `up -d --no-build` (D-31).
  Se o D-17 escolheu build na VM: `build ml-service`, **depois** `build backend` — em paralelo
  estoura os 4 GB (§9.3). Se escolheu registry: `docker compose pull`.
  📌 **Com a opção (c) recomendada, esta task some da instância:** o build acontece na máquina local
  (passo 1 do [`docs/deploy-runbook.md`](docs/deploy-runbook.md)), onde já rodou no D-04 sem
  restrição de memória. Na VM sobra `docker load` (D-28) e `up -d --no-build` (D-31). É o principal
  ganho da decisão — o §9.3 deixa de ser risco de deploy.
  _Depende de: D-28_

- [x] **D-31 — `up -d` e healthchecks internos** `A`
  ✅ **Feito em 2026-09-13.** Cinco containers `running`; `db`, `ml-service` e `backend`
  `healthy` em ~34s. Healthchecks por dentro (§9.6): backend devolve `{"status":"UP"}` e o
  ml-service `{"status":"ok","service":"ml-service","version":"1.0.0"}` pela rede interna.
  **R6 provado na nuvem:** `docker port` volta vazio para `db`, `ml-service` e `backend` —
  só o Caddy publica portas. `GET http://107.20.236.251/` → 200.
  Subir, conferir `ps` (todos `running`, `db` e `ml-service` `healthy`) e bater nos healthchecks
  por dentro (§9.6). O `/actuator/health` do backend só existe depois do D-12.
  _Depende de: D-29, D-30_

- [~] **D-32 — Certificado TLS emitido** `A` `adiada com a D-18`
  ⏸️ **Adiada junto com o D-18 (2026-09-13).** O `04-subir.sh` subiu com `SITE_ADDRESS=:80`,
  o modo HTTP puro do `Caddyfile:18` — o Let's Encrypt não emite certificado para endereço
  IP (§5). Quando houver domínio: `infra/scripts/04-subir.sh <dominio>` troca o
  `SITE_ADDRESS` e reinicia o Caddy, sem recriar nada na AWS.
  ⚠️ **Obrigatória antes da defesa.** Sem HTTPS o JWT trafega em claro (§1.7), o navegador
  mostra "Não seguro" e o D-45 pede o cadeado nas capturas.
  `https://<domínio>` com cadeado válido, e `http://` redirecionando sozinho.
  ⚠️ **Rate limit do Let's Encrypt: 5 falhas por hora por hostname.** Se o DNS não estava propagado
  no primeiro `up`, o ACME falha; repetir às cegas queima a cota e você fica uma hora sem conseguir
  emitir. Conferir o DNS antes, e ler `docker compose logs caddy` ao primeiro erro.
  Confirmar também que o volume `caddy_data` persiste — sem ele, cada `up` pede certificado novo.
  _Depende de: D-31_

---

## Épico D5 — Validação ponta a ponta em produção `Trilha A+B`

> **É aqui que as duas trilhas se encontram.** Antes do `tasks-integracao.md` fechar, só o D-33 roda.

- [x] **D-33 — Fumaça pela API** `A`
  ✅ **Feito em 2026-09-13** pelo `05-fumaca.sh`, contra a URL de produção. Login ok;
  importação de **10 produtos** e **1.690 linhas de vendas / 180 dias**, zero erros; motor
  com **10/10 processados e 0 falhas**; `/dashboard`, `/alertas`, `/curva-abc`, `/produtos`,
  `/produtos/1/detalhe` e `/produtos/1/metricas` todos **200**.
  🎯 **O que mais importa para o TCC:** as métricas da T10 vieram reais da EC2 — Prophet
  **MAPE 14,18%** (`selecionado: true`) contra Holt-Winters **55,74%**. O pin do
  `cmdstanpy==1.2.4` (D-46) atravessou o `docker save`/`load` intacto, então **a comparação
  de modelos na nuvem é válida** e não um fallback silencioso para Holt-Winters.
  **Valida a trilha A inteira sem depender do frontend.**
  Rodar a coleção `docs/postman/StockSense_E2E.postman_collection.json` contra a URL de produção:
  login → `POST /api/importacao/produtos` → `/vendas` → `POST /api/motor/recalcular` → conferir
  dashboard, alertas, curva ABC e métricas. **Valida a trilha A inteira sem depender do frontend.**
  _Depende de: D-32_

- [~] **D-34 — Fluxo completo pela interface** `A+B` `T3 validada; faltam as demais telas`
  🔶 **Parcialmente validado em 2026-09-13 — a T3 passou pelo navegador, em produção.**
  O lojista subiu `produtos.xlsx` e `vendas.xlsx` pela tela de Importação e clicou em
  processar. Funcionou ponta a ponta: upload multipart atravessando o Caddy, parsing do
  xlsx pelo POI, validação, persistência e disparo do motor.

  Produto importado pela interface: **id 12, "Achocolatado em Pó 400g"** (170 linhas de
  vendas, 180 dias). O motor calculou demanda de 12,67 un/dia, ponto de reposição 63,31 e
  **1,58 dias até ruptura** — contra os ~1,6 projetados a partir da massa gerada, ou seja,
  o motor recuperou a demanda que o gerador injetou.

  Três coisas que este teste provou e que a fumaça por API (D-33) não provava:
  1. **Acentuação sobrevive** ao caminho navegador → multipart → POI → MySQL → JSON
     ("Achocolatado em Pó", "Pão Francês" corretos na resposta).
  2. **A ABC é relativa e recalculada no backend** (ADR #3): o produto novo entrou em
     **1º lugar** por faturamento (R$ 62.953,13) e tirou a liderança do Arroz 5kg
     (R$ 61.452,60), reordenando a curva inteira.
  3. **A importação é incremental** — produtos fazem upsert por `produto_id` e vendas são
     acrescentadas. Dá para crescer o catálogo sem reimportar tudo.
     ⚠️ Corolário: reimportar o MESMO arquivo de vendas **duplica** as linhas, porque não
     há deduplicação. Produtos são seguros de reimportar; vendas não.

  **O que falta para fechar:** percorrer as demais telas (T2, T4, T5, T6, T7, T10) com o
  console aberto, e exercitar os estados `null` — que exigem banco com dados e **sem** o
  motor rodado, situação que não existe mais em produção.
  O mesmo roteiro pelo navegador, com o mock desligado por padrão (D-11). Critério: sem erro no
  console, e os dados batendo com os do D-33.
  Testar **também antes de rodar o motor**, para exercitar os estados `null` — o
  `tasks-integracao.md` avisa que todo campo calculado vem `null` até o primeiro recálculo.
  _Depende de: D-33, D-11, `tasks-integracao.md` I-11_

- [~] **D-35 — Cronometrar o lote real** `A` `parcial: 10 SKUs`
  🔶 **Medido em 2026-09-13, mas com catálogo pequeno.** `POST /api/motor/recalcular` levou
  **5 s para 10 produtos = 0,50 s/produto** na t3.medium. Comparação das três medições:

  | Ambiente | s/produto |
  |---|---|
  | Desktop 12 CPUs, fora do Docker (D-41) | 0,42–0,53 |
  | Docker local, 3,95 GB (2026-09-12) | 0,40 |
  | **t3.medium, produção** | **0,50** |

  A instância pequena fica **dentro da mesma faixa** do desktop. Projeção para 312 SKUs:
  **~2,6 min**, coerente com os ~2,8 min do D-41 e muito abaixo dos **5 a 25 min do R1** —
  que sai definitivamente da lista de riscos.
  ⚠️ **Segue `[~]`:** 10 produtos não exercitam pressão de memória nem consumo de crédito de
  CPU como 312 exercitariam. O tempo por produto é sólido; o tempo total do lote real, não.
  Medir `POST /api/motor/recalcular` com o catálogo completo na t3.medium. É o número que confirma
  (ou derruba) a estimativa de 5–25 min do R1, e ele vai para a metodologia do TCC.
  _Depende de: D-33_

---

## Épico D6 — Operação `Trilha A`

- [x] **D-36 — `infra/scripts/backup.sh` versionado** `A`
  **Feito em 2026-09-12.** Arquivo em [`infra/scripts/backup.sh`](../scripts/backup.sh).
  Lê o nome do bucket de `/etc/stocksense-backup.conf` (tem sufixo aleatório, vem do
  output `bucket_backup` do D-24) e a senha do root do `.env` da instância. Acrescentei
  sobre o bloco do §9.7: `--single-transaction` (dump consistente sem travar escrita) e
  **verificação de dump vazio** — sem ela, uma falha de autenticação no MySQL produziria
  um `.gz` de poucos bytes que o `aws s3 cp` subiria como se fosse backup bom. Também
  confere o objeto no S3 com `s3 ls` antes de sair com 0, para o cron reportar falha.
  ⚠️ O `s3://stocksense-backup/` do §9.7 está errado: o bucket tem sufixo aleatório.
  Hoje o script existe **só como bloco de código no §9.7**. Virar arquivo de verdade, recebendo o
  nome do bucket por variável de ambiente (ele tem sufixo aleatório — output do D-24) e a senha do
  root por `.env`. `mysqldump` → `gzip` → `aws s3 cp`. A instance profile autentica: **nenhuma
  access key no disco.**
  _Depende de: D-24_

- [ ] **D-37 — Agendar o backup** `A` `destravada`
  ✅ **Destravada em 2026-09-13.** O S3 saiu do Terraform e o `backup.sh` passou a criar o
  bucket sozinho (ver D-24). Segue sem `lifecycle`, então dumps antigos não expiram — limpar
  à mão de tempos em tempos, ou aceitar o acúmulo num projeto de TCC.
  Instalar em `/etc/cron.daily/`. Confirmar que o objeto aparece no S3 no dia seguinte.
  _Depende de: D-36, D-31_

- [ ] **D-38 — Testar a restauração** `A`
  Backup não testado não é backup. Baixar um dump e restaurar num MySQL descartável, conferindo a
  contagem de linhas de `produto` e `venda`.
  _Depende de: D-37_

- [x] **D-39 — Runbook de ligar/desligar** `A`
  ✅ **Feito em 2026-09-13.** Runbook em [`infra/docs/ligar-desligar.md`](docs/ligar-desligar.md),
  com os ids reais e a tabela de custo.
  **Verificado na prática, que era o ponto da task** — ciclo completo medido com comparação
  do estado antes e depois:

  | Etapa | Tempo |
  |---|---|
  | `stop` → `stopped` | 32 s |
  | indisponibilidade confirmada | conexão recusada ✓ |
  | `start` → `running` | 11 s |
  | SSH respondendo | 11 s depois |
  | containers no ar | **automático, sem nenhum comando** |
  | HTTP 200 pela borda | imediato |

  **Indisponibilidade total: pouco menos de 1 minuto.** Os 12 produtos voltaram com os
  mesmos ids, o mesmo líder da ABC (Achocolatado, R$ 62.953,13) e mesmos estoque e classe
  produto a produto — comparação campo a campo, não só de contagem. O Elastic IP não mudou.
  É a demonstração empírica do §7.2, e vira material de defesa.
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

- [~] **D-43 — Memória real sob carga** `A` `parcial: 10 SKUs`
  🔶 **Primeira medição na instância, 2026-09-13**, logo após o lote do D-33:

  | Container | Uso | Limite | % |
  |---|---|---|---|
  | `db` | 420,9 MiB | 600 MiB | **70,2%** |
  | `backend` | 309,6 MiB | 1 GiB | 30,2% |
  | `ml-service` | 296,1 MiB | 1,758 GiB | 16,5% |
  | `caddy` + `frontend` | 17,6 MiB | — | — |

  Instância: **1,6 GiB usados de 3,7 GiB**, 2,2 GiB disponíveis. **Swap praticamente
  intocado — 76 KiB de 2,0 GiB.** Disco em 30% dos 29 GB.
  Os números batem com o ensaio local do D-07, o que valida o orçamento do §6.1 e confirma
  o `db` como o container mais apertado.
  ⚠️ **Segue `[~]` pelo mesmo motivo do D-35 e do D-07:** com 10 produtos não houve carga.
  Fecha de verdade com catálogo de ~312 SKUs.
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
| ~~D-11 (mock off)~~ | ✅ resolvida — 10/11 das I-xx concluídas e mergeadas (PR #10) | `frontend/docs/tasks-integracao.md` |
| D-34 (fluxo pela UI) | I-11 (fumaça E2E no navegador) — **única I-xx aberta** | `frontend/docs/tasks-integracao.md` |
| ~~D-09 (`API_BASE_URL`)~~ | ✅ resolvida sem conflito com a I-02: o proxy no nginx de dev deixa `/api` válido nos dois ambientes | `frontend/nginx-dev.conf` |
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
