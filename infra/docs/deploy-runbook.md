# Runbook de deploy — StockSense

> **O que é este documento.** O passo a passo executável de como o StockSense sobe na EC2, na
> forma decidida na **D-17**: as imagens são construídas na máquina local e chegam prontas na
> instância; a t3.medium nunca compila nada.
>
> **Como usar.** Cada passo tem o comando, **o que ele faz** e **como saber que deu certo**. Os
> comandos marcados `[local]` rodam na sua máquina; os marcados `[via ssh]` rodam na VM mas são
> disparados da sua máquina — você não precisa trabalhar dentro da instância.
>
> **Estado em 2026-09-13: executado com sucesso.** O sistema está no ar em
> http://107.20.236.251. Os passos abaixo foram validados na prática e depois automatizados
> em [`infra/scripts/`](../scripts/README.md) — **prefira os scripts**; este documento
> continua valendo como referência do que cada um faz por dentro, e para diagnóstico quando
> algum passo falhar.
>
> Divergências entre o que está aqui e o que foi executado de fato:
> - O passo 6 subiu com `SITE_ADDRESS=:80` (HTTP puro no IP), não com domínio — decisão D-18.
> - O `.env` do passo 4 é gerado pelo `04-subir.sh` na própria instância, com `openssl rand`.
> - O tarball do passo 2 saiu com **350 MB**, não os ~385 MB estimados.
>
> Referências: [`infra/README.md`](../README.md) (ponto de entrada e restrições do Learner
> Lab), `infra/tasks.md` (backlog, D-17 a D-32), `infra/infraestrutura-nuvem.md`
> (arquitetura, riscos, orçamento).

---

## 1. A ideia em um parágrafo

Uma imagem Docker separa **build-time** de **run-time**. Baixar bibliotecas — `pip install` no
ml-service, `gradle bootJar` no backend — acontece no build. Rodar acontece depois, num sistema de
arquivos onde essas bibliotecas já estão instaladas. Como a imagem gerada é a mesma
independentemente de onde foi construída, não há razão para a t3.medium fazer o trabalho caro: ela
recebe o resultado pronto.

Consequências práticas:

- A VM **não** executa `pip install` nem `gradle`. Não precisa de acesso ao PyPI nem ao Maven
  Central. Precisa de rede de saída apenas para o Let's Encrypt (D-32) e o S3 do backup (D-36).
- O risco do §9.3 — build do Gradle estourando os 4 GB da instância — **deixa de existir**, porque
  o build não acontece lá.
- O pin `cmdstanpy==1.2.4` (D-46) é gravado na imagem no momento do build. A VM não teria como
  corrigi-lo depois, porque ela não instala nada. Daí a gravidade daquela task.

### O que roda onde

| | Máquina local | EC2 |
|---|---|---|
| `docker build` (compila Kotlin, instala Python) | ✅ | ❌ nunca |
| `docker save` / transferência | ✅ | — |
| `docker load` | disparado daqui | executa lá |
| `docker compose up` | disparado daqui | executa lá |
| Arquivos de config e front (`Caddyfile`, `docker-compose.prod.yml`, `frontend/web`) | — | `git clone` / `git pull` |

### Por que os arquivos ainda precisam ir para a VM

O `docker-compose.prod.yml` usa dois bind mounts:

```yaml
- ./Caddyfile:/etc/caddy/Caddyfile:ro
- ./frontend/web:/usr/share/nginx/html:ro
```

Bind mount lê do disco da instância. Então o repositório (ou ao menos esses arquivos) precisa
existir lá, **independentemente** de como as imagens chegam. Isso vale para as três opções
avaliadas — não é um custo específico desta.

O lado bom: o front é servido direto do disco, então **atualizar as telas é um `git pull`**, sem
rebuild, sem transferência de imagem e sem restart. Com a trilha B em 0/11, essa vai ser a operação
mais frequente até a defesa.

---

## 2. Pré-requisitos

Antes do passo 1, estas coisas precisam estar resolvidas:

| Item | Task | Estado em 2026-09-06 |
|---|---|---|
| Domínio escolhido e apontado para o Elastic IP | D-18, D-26 | ❌ decisão pendente |
| `terraform apply` executado, instância no ar | D-24 | ❌ |
| Bootstrap confirmado (Docker, swap, AWS CLI) | D-27 | ❌ |
| `stocksense-key.pem` em mãos | D-24 | ❌ gerado pelo apply |
| Imagens buildadas e validadas localmente | D-04 | ✅ feito |

⚠️ **O DNS precisa estar propagado antes do passo 6.** O Let's Encrypt limita a **5 falhas por
hora por hostname**. Se o Caddy tentar emitir com o DNS ainda apontando para o lugar errado, cada
tentativa queima cota — e repetir às cegas deixa você uma hora sem conseguir emitir. Confirme com
`nslookup <domínio>` antes.

---

## 3. Passo a passo — primeiro deploy

### Passo 1 · Construir as imagens `[local]`

```bash
cd <raiz do repo>
docker compose -f docker-compose.prod.yml --env-file .env.ensaio build
```

**O que faz.** Compila o Kotlin em um fat jar e instala as dependências Python, produzindo
`stocksense-backend:prod` e `stocksense-ml:prod`.

**Por que o `--env-file` aqui.** O compose valida as variáveis `${VAR:?}` mesmo em `build`. O
`.env.ensaio` (D-03) serve — nenhuma credencial dele entra na imagem; ele só satisfaz a validação.

**Como saber que deu certo.**

```bash
docker images | grep stocksense
# stocksense-backend:prod   ~273MB
# stocksense-ml:prod        ~685MB
```

**Verificação que vale o minuto** — confirma que o Prophet está funcional na imagem (D-46), a falha
que não dá erro:

```bash
docker run --rm --network none stocksense-ml:prod pip show cmdstanpy | grep Version
# Version: 1.2.4
```

Se aparecer outra versão, **pare aqui**: o motor cairia em fallback silencioso para Holt-Winters e a
comparação de modelos (T10) seria inválida sem nenhum erro visível.

---

### Passo 2 · Empacotar `[local]`

```bash
docker save stocksense-backend:prod stocksense-ml:prod | gzip > stocksense-imgs.tar.gz
```

**O que faz.** `docker save` exporta as imagens do armazenamento interno do Docker para um `.tar`
— não dá para copiar uma imagem com `cp`, porque ela é um conjunto de camadas num banco interno,
não um arquivo. O `gzip` reduz a transferência.

**Tamanho medido em 2026-09-06:** **385 MB** com `gzip -1`. Com `gzip -9` cai mais, ao custo de CPU.

**Guarde este arquivo.** Sem registry, ele é o seu rollback — ver §5.

---

### Passo 3 · Levar os arquivos de config para a VM `[via ssh]`

```bash
ssh -i stocksense-key.pem ubuntu@<ip> 'git clone https://github.com/tcc-stocksense/code.git ~/stocksense'
```

**O que faz.** Coloca na instância o `docker-compose.prod.yml`, o `Caddyfile` e o `frontend/web`
que os bind mounts precisam.

⚠️ **Se o repositório for privado**, isto pede deploy key ou PAT na instância. Alternativa sem
credencial na VM — copiar apenas o necessário:

```bash
scp -i stocksense-key.pem docker-compose.prod.yml Caddyfile ubuntu@<ip>:~/stocksense/
scp -i stocksense-key.pem -r frontend/web ubuntu@<ip>:~/stocksense/frontend/
```

O custo dessa alternativa: o redeploy do front deixa de ser `git pull` e passa a ser `scp`.

---

### Passo 4 · Criar o `.env` de produção `[via ssh]` — D-29

```bash
ssh -i stocksense-key.pem ubuntu@<ip> 'cat > ~/stocksense/.env && chmod 600 ~/stocksense/.env' <<EOF
DB_ROOT_PASSWORD=<senha nova e forte>
DB_USERNAME=appuser
DB_PASSWORD=<senha nova e forte>
JWT_SECRET=$(head -c 32 /dev/urandom | base64)
SITE_ADDRESS=<domínio do D-18>
EOF
```

**O que faz.** Cria o único arquivo que precisa nascer na instância. As cinco variáveis são
obrigatórias: o compose usa `${VAR:?}` e **aborta** se faltar qualquer uma.

⚠️ **Valores novos, nunca os do `.env.ensaio`.** O ensaio usa senhas descartáveis, por definição.

⚠️ **`SITE_ADDRESS` é o domínio real aqui** (não `:80`). É ele que faz o Caddy buscar o
certificado — por isso o DNS precisa estar propagado antes.

---

### Passo 5 · Carregar as imagens na VM `[via ssh]`

```bash
gunzip -c stocksense-imgs.tar.gz | ssh -i stocksense-key.pem ubuntu@<ip> 'docker load'
```

**O que faz.** `docker load` importa o `.tar` de volta para o armazenamento interno do Docker, na
instância. O arquivo viaja pelo próprio túnel SSH — não precisa de `scp` separado nem sobra cópia
no disco da VM.

**Como saber que deu certo.** A saída lista as imagens carregadas:

```
Loaded image: stocksense-backend:prod
Loaded image: stocksense-ml:prod
```

---

### Passo 6 · Subir `[via ssh]` — D-31, D-32

```bash
ssh -i stocksense-key.pem ubuntu@<ip> \
  'cd ~/stocksense && docker compose -f docker-compose.prod.yml up -d --no-build'
```

**O que faz.** Sobe os cinco containers. O `--no-build` é uma trava deliberada: o compose declara
`image:` junto de `build:`, então ele usaria a imagem carregada de qualquer forma — mas com a flag,
um erro de tag falha alto em vez de disparar silenciosamente um build de Gradle na t3.medium.

**Como saber que deu certo.**

```bash
ssh -i stocksense-key.pem ubuntu@<ip> 'cd ~/stocksense && docker compose -f docker-compose.prod.yml ps'
```

Critério: cinco containers `running`, com `db`, `ml-service` e `backend` `healthy`. O backend
demora — `start_period` de 90 s, porque o Flyway roda as migrations na subida.

**TLS (D-32).** Na primeira subida o Caddy vai ao Let's Encrypt sozinho. Ao primeiro erro, **leia
o log antes de repetir** — cada tentativa falha consome a cota de 5/hora:

```bash
ssh -i stocksense-key.pem ubuntu@<ip> 'cd ~/stocksense && docker compose -f docker-compose.prod.yml logs caddy | tail -30'
```

---

### Passo 7 · Validar `[local]` — D-33

```bash
curl -I https://<domínio>/                    # 200, e cadeado válido no navegador
curl -X POST https://<domínio>/api/auth/login \
     -H 'Content-Type: application/json' -d '{"email":"x@x.com","senha":"errada"}'
```

**Critério.** A raiz devolve o front; o login devolve `application/problem+json`. Esse content-type
é a prova de que a requisição chegou no **backend** e não num 404 do nginx — foi assim que o D-06
validou o roteamento no ensaio local.

📌 **Anotado no D-06:** credencial inválida devolve **404**, não 401. É o comportamento atual do
backend; a trilha B precisa tratar 404 no login como "credencial inválida".

Depois disto, rodar a coleção `docs/postman/StockSense_E2E.postman_collection.json` contra a URL de
produção fecha o D-33 e valida a trilha A inteira, sem depender do frontend.

---

## 4. Redeploy — o que fazer conforme o que mudou

| Mudou | Passos | Custo |
|---|---|---|
| Front (`frontend/web`) | `ssh ... 'cd ~/stocksense && git pull'` | segundos, sem restart |
| `Caddyfile` / compose | `git pull` + passo 6 | segundos |
| Backend ou ml-service | passos 1, 2, 5, 6 | ~5 min, dominado pelo upload |

O front não passa por imagem — é bind mount, o nginx serve o arquivo novo na requisição seguinte.

---

## 5. Rollback

Sem registry, não existe histórico central de imagens. Duas formas de ter para onde voltar:

**Taguear por data antes de empacotar** `[local]`:

```bash
docker tag stocksense-backend:prod stocksense-backend:2026-09-06
docker tag stocksense-ml:prod      stocksense-ml:2026-09-06
```

Com a tag carregada na VM, voltar é local e instantâneo:

```bash
ssh -i stocksense-key.pem ubuntu@<ip> \
  'docker tag stocksense-backend:2026-09-06 stocksense-backend:prod && cd ~/stocksense && docker compose -f docker-compose.prod.yml up -d --no-build'
```

**Guardar o `.tar.gz` do último deploy que funcionou.** Se a VM for perdida, é dele que você
recomeça, sem precisar rebuildar.

Os 30 GB de EBS comportam várias versões — cada par de imagens ocupa ~1 GB descompactado.

---

## 6. As outras opções avaliadas na D-17

Todas as três resolvem **dois problemas distintos** que o backlog original tratava como um só:

- **Eixo 1 — onde as imagens são construídas.** É onde mora o risco de memória do §9.3.
- **Eixo 2 — como os arquivos de config e o front chegam à VM.** Inevitável nas três, por causa dos
  bind mounts.

### (a) `git clone` na VM + `docker compose up --build`

Opção (a) do backlog. Resolve os dois eixos com um comando só, e o redeploy do front é `git pull`.

**Contra.** Concentra na instância justamente o passo que pode falhar: o §9.3 avisa que o build do
Gradle pode estourar os 4 GB da t3.medium, e o backlog recomenda buildar uma imagem por vez para
não estourar. Diagnosticar um OOM de Gradle por SSH é caro. Exige deploy key se o repo for privado.

### (b) Registry (ECR ou Docker Hub) + `docker compose pull`

Opção (b) do backlog. Elimina o build na VM e dá histórico de imagens com rollback por tag —
tecnicamente a mais correta das três.

**Contra.** É a que tem mais peças móveis: o ECR **não está no Terraform** (precisa ser escrito),
exige autenticação na instância e renovação de token, e ainda assim não resolve o eixo 2. Para uma
instância única de TCC, o custo de montagem não se paga.

### (c) `docker save` → SSH → `docker load` — **escolhida**

Não estava no backlog. Viabilizada por uma medição do D-04: as imagens ficaram em **273 MB + 685 MB
(385 MB comprimidos)**, contra os 1,5–2,5 GB que o R4 projetava para o ml-service — o que tornaria a
transferência impraticável.

**A favor.** Nenhum build na instância, nenhum registry, nenhuma credencial de repositório na VM
para as imagens. Todos os comandos são disparados da máquina local, então diagnosticar erro não
exige trabalhar dentro da instância. O compose já suporta sem alteração, porque declara `image:`
junto de `build:`.

**Contra, e assumido.** Sem histórico central de imagens — o rollback depende de tags locais e do
`.tar.gz` guardado (§5). Depende do upload da sua conexão: 385 MB a cada mudança de backend ou
ml-service (mudanças de front não transferem nada).

### Comparação

| | (a) build na VM | (b) registry | (c) save/load |
|---|---|---|---|
| Build na t3.medium (risco §9.3) | **sim** | não | não |
| Infra nova a escrever | nenhuma | ECR + IAM no Terraform | nenhuma |
| Credencial nova na VM | deploy key (se privado) | login do registry | nenhuma p/ imagens |
| Onde se diagnostica uma falha | na instância | nos dois lados | na máquina local |
| Rollback | rebuild | por tag, central | tag local + `.tar.gz` |
| Transferência por deploy de código | ~0 (git) | ~385 MB | ~385 MB |
| Redeploy de front | `git pull` | `git pull` | `git pull` |

---

*Decisão registrada na D-17 do `infra/tasks.md`. Os passos deste runbook são o conteúdo das*
*D-28 (levar código/imagens) e D-30 (build). O runbook de operação — ligar, desligar, custo — é a*
*D-39, e só faz sentido escrever quando a instância existir e tiver `instance_id` real.*
