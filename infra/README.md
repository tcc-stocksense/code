# Infraestrutura — comece por aqui

> Ponto de entrada da pasta `infra/`. Orienta quem chega sem contexto: **o que existe hoje**,
> **o que já foi decidido**, **o que o ambiente impõe** e **como provisionar do zero**.
> Os detalhes ficam nos documentos linkados — este arquivo não os repete.
>
> Última atualização: **2026-09-13**.

---

## 1. Estado atual

**O StockSense está no ar** em http://107.20.236.251 — HTTP puro, sem domínio (ver §3).

| | |
|---|---|
| Instância | `i-01fb1975491b85fb1` · t3.medium · us-east-1 |
| Elastic IP | `107.20.236.251` |
| VPC / SG | `vpc-028883f4797082259` / `sg-0d1a8c54d9a4d292d` |
| Bucket S3 | `stocksense-backup-6a9ff8eb` (criado, mas incompleto — ver §4) |
| Branch | `chore/infra-terraform-aws` |
| Dados | 12 produtos, ~53 mil linhas de vendas, motor executado |

Cinco containers na instância: `caddy` (único com porta publicada), `frontend`, `backend`,
`ml-service`, `db`. Validado em produção: importação pela API e pela interface, motor sem
falhas, e as métricas da T10 com **Prophet ativo de verdade** (MAPE 14,18% × Holt-Winters
55,74%) — não o fallback silencioso que invalidaria o núcleo acadêmico do TCC.

---

## 2. Mapa dos documentos

| Arquivo | Para quê |
|---|---|
| **este README** | orientação e plano de provisionamento |
| [`infraestrutura-nuvem.md`](./infraestrutura-nuvem.md) | o desenho, os custos, os riscos e as justificativas |
| [`tasks.md`](./tasks.md) | backlog de execução (D-01…D-46), com estado e histórico de cada decisão |
| [`scripts/README.md`](./scripts/README.md) | ordem dos scripts e pré-requisitos |
| [`docs/deploy-runbook.md`](./docs/deploy-runbook.md) | o passo a passo **manual**, equivalente ao que os scripts automatizam |
| [`docs/ligar-desligar.md`](./docs/ligar-desligar.md) | parar e religar a instância, com a verificação prática |

**Em caso de conflito, o `CLAUDE.md` da raiz prevalece.**

---

## 3. As decisões que moldaram tudo

Não precisam ser rediscutidas. Cada uma mudou a forma dos scripts, e o registro completo
com alternativas avaliadas está no `tasks.md`.

**D-17 — O build acontece na máquina local, nunca na EC2.** As imagens viajam como
`.tar.gz` (350 MB, medido) e entram por `docker load`. A t3.medium tem 4 GB e o Gradle
compilando lá dentro era o risco mais caro do projeto: depurar OOM por SSH é lento e caro.
Os arquivos de configuração chegam por `git clone`, porque o compose de produção monta
`Caddyfile` e `frontend/web` como bind mount — o repositório é público, sem deploy key.

**D-18 — A primeira subida é HTTP puro no IP**, com `SITE_ADDRESS=:80`. O Let's Encrypt
não emite certificado para endereço IP, então exigir TLS na primeira subida traria
propagação de DNS e o limite de 5 falhas/hora do ACME para o caminho crítico — dois jeitos
de perder uma manhã por algo que não é a infraestrutura. **Continua obrigatório antes da
defesa:** sem HTTPS o JWT trafega em claro.

**D-09 — O frontend usa caminho relativo.** `API_BASE_URL` é `/api` nos dois ambientes: em
produção o Caddy serve o estático e faz proxy de `/api`; em desenvolvimento o nginx ganhou
a mesma rota (`frontend/nginx-dev.conf`). Mesma origem nas duas pontas, sem detecção de
ambiente e sem CORS.

**ADR #3 — A classificação ABC roda no backend.** Confirmado empiricamente em produção: ao
importar um produto novo, ele assumiu o 1º lugar e reordenou a curva inteira. A ABC é
ranking relativo entre todo o catálogo, e o `/predict` do ml-service é por produto.

---

## 4. O que o AWS Academy Learner Lab impõe

A conta **não é uma conta AWS comum** — o §7 do `infraestrutura-nuvem.md` assumia que era.
Cinco restrições, todas descobertas na prática:

| Restrição | Consequência |
|---|---|
| `iam:CreateRole` negado | O Terraform **não cria role**; usa a `LabRole` pronta, via `var.instance_profile_name = "LabInstanceProfile"`. Perde-se o privilégio mínimo de `s3:PutObject` |
| `budgets:*` negado | Sem alarme de orçamento (D-23). O controle de gasto é o painel do lab |
| `s3:GetBucketObjectLockConfiguration` negado por SCP | ⛔ **Bloqueador ativo.** Ver abaixo |
| Credenciais temporárias | Expiram em ~3–4 h e exigem `AWS_SESSION_TOKEN`. Recolar a cada sessão |
| Sessão do lab encerra | O lab **para a instância**. Disco e IP persistem; os containers voltam sozinhos |

✅ **`t3.medium` é permitida** — era a maior incógnita, confirmada no apply.

### ⛔ Bloqueador: o S3 quebra qualquer apply futuro

O provider da AWS lê a configuração de *object lock* logo após criar um bucket, e a SCP da
organização do lab nega essa leitura. O apply **cria o bucket e aborta em seguida**, sem
aplicar bloqueio de acesso público, criptografia e **lifecycle**.

Efeito prático: os dados estão seguros (a AWS aplica bloqueio público e SSE-S3 por padrão
desde 2023), mas **dumps antigos não expiram sozinhos**, e **todo `terraform apply` daqui
em diante falha no mesmo ponto** enquanto esses três recursos estiverem na configuração.

**Resolver antes de qualquer novo apply:** remover `aws_s3_bucket_public_access_block`,
`aws_s3_bucket_server_side_encryption_configuration` e `aws_s3_bucket_lifecycle_configuration`
de `terraform/backup.tf`, e configurar o bucket pelo console se o lifecycle for necessário.

---

## 5. Provisionar do zero

Tudo é disparado **da máquina local**. Os scripts são idempotentes: reexecutar não estraga
o que já funcionou.

### Antes de começar

1. Iniciar a sessão do Learner Lab e esperar o indicador ficar verde
2. **AWS Details → AWS CLI → Show**, e colar as três linhas em `infra/lab-credentials.env`
   (gitignorado). O script aceita o formato `[default]` com minúsculas que a AWS exibe
3. Confirmar o nome da instance profile em **IAM → Roles → LabRole → "Instance profile ARNs"**
4. Abrir o Docker Desktop (necessário no passo 1)

### A sequência

```bash
infra/scripts/01-empacotar-imagens.sh    # build local + docker save (~350 MB)
infra/scripts/02-provisionar.sh          # plan + conferências — NADA é criado
infra/scripts/02-provisionar.sh --apply  # cria a infra na AWS
#  >>> copiar terraform.tfstate e stocksense-key.pem para FORA do repositório
infra/scripts/03-enviar.sh               # git clone na VM + scp + docker load
infra/scripts/04-subir.sh                # .env de produção + up -d + healthchecks
infra/scripts/05-fumaca.sh               # login → importação → motor → KPIs
```

**Tempo total: ~50 min**, quase todo no passo `03` — o upload dos 350 MB é a única
incógnita real, e depende da conexão.

### O que observar em cada passo

| Passo | Atenção |
|---|---|
| `01` | Se avisar que o `cmdstanpy` não é **1.2.4**, **pare**: o Prophet cairia em fallback silencioso e a comparação de modelos (T10) ficaria inválida sem erro visível |
| `02` | O script barra NAT Gateway, EIP duplicado, porta interna exposta e criação de role IAM — mas a leitura do plano é sua |
| `--apply` | É aqui que o lab recusa tipo de instância, se for o caso |
| **tfstate** | O state guarda a **chave SSH privada em texto claro**, e é o que permite `terraform destroy` limpo. Ambos são gitignorados — e é por isso que somem com um `git clean -xdf` |
| `03` | Passo longo. Acompanhe com `ls -lh` do tarball na VM |
| `05` | Cronometra o lote: esse número vai para a metodologia do TCC |

### Depois de provisionar

O `.outputs.env` (IP, instance id, bucket, caminho do `.pem`) é gravado pelo `02` e lido
pelos passos seguintes. **Se o apply falhar no S3 e abortar, ele não é escrito** — gere à
mão a partir de `terraform output`.

---

## 6. Armadilhas que já custaram tempo

- **`05-fumaca.sh` só serve para banco limpo.** As vendas são acrescentadas sem
  deduplicação: rodá-lo sobre um banco que já tem os dados duplica 1.690 linhas e dobra a
  demanda calculada. Produtos são seguros, porque fazem upsert por `produto_id`
- **O `.env` de produção só é criado uma vez.** O MySQL aplica usuário e senha apenas na
  primeira inicialização do volume — regerar depois quebra a autenticação do backend sem
  aparecer em log nenhum
- **`docker compose` precisa de `--env-file`** mesmo para `ps`: o compose de produção usa
  `${VAR:?}` e aborta na interpolação antes de fazer qualquer coisa
- **Os `.sh` são fixos em LF** pelo `.gitattributes`. Com `core.autocrlf=true`, o checkout
  os converteria para CRLF e o bash morreria com `$'\r'` — inclusive dentro dos heredocs
  que os scripts mandam por SSH
- **O IP residencial muda.** A regra de SSH é `/32`. Se o SSH parar de conectar depois de
  um tempo, rode o `02` de novo, que redescobre o IP

---

## 7. O que falta

| | |
|---|---|
| **Antes da defesa** | HTTPS com domínio · snapshot do EBS · capturas e diagramas finais |
| **Bloqueado** | Backup para S3 — depende de resolver a SCP do §4 |
| **Precisa de dados reais** | Medições de carga com ~312 SKUs: tempo do lote, memória e crédito de CPU. Use `ml-service/app/tests/generate_catalogo.py` |
| **Higiene** | A credencial semeada (`admin@stocksense.local` / `admin123`) está num repositório público e o sistema está exposto. Manter a instância desligada fora das demonstrações, ou trocar a senha por `UPDATE` |

Estado detalhado de cada tarefa: [`tasks.md`](./tasks.md).
