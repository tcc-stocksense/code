# Scripts de deploy

Ordem de execução. Todos são disparados **da sua máquina** (exceto o
`backup.sh`, que roda na instância) e todos são idempotentes: reexecutar não
estraga o que já funcionou.

| # | Script | Tasks | O que faz |
|---|---|---|---|
| 0 | — | `D-07`, `I-11` | Ensaio local: stack de produção na sua máquina, com dados |
| 1 | `01-empacotar-imagens.sh` | `D-28` | Build local + `docker save` → `infra/dist/` (~385 MB) |
| 2 | `02-provisionar.sh` | `D-21`→`D-24` | `tfvars` + `plan` + conferências; aplica só com `--apply` |
| 3 | `03-enviar.sh` | `D-27`, `D-28` | Confere o bootstrap, `git clone` na VM, `scp` + `docker load` |
| 4 | `04-subir.sh` | `D-29`, `D-31` | `.env` de produção, `up -d --no-build`, healthchecks |
| 5 | `05-fumaca.sh` | `D-33`, `D-35` | Login → importação → motor (cronometrado) → KPIs |
| — | `backup.sh` | `D-36`, `D-37` | `mysqldump` → S3, via cron na instância |

## Antes de começar

**Credenciais do Learner Lab** em `infra/lab-credentials.env` (gitignorado).
São **temporárias** — expiram ao fim da sessão do lab e mudam quando ele é
reiniciado. Pegue em "AWS Details" → "AWS CLI" e cole as três linhas:

```
AWS_ACCESS_KEY_ID=ASIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
```

**Confirme a instance profile.** O Learner Lab nega `iam:CreateRole`, então o
Terraform usa a role que o lab já fornece. O nome padrão assumido é
`LabInstanceProfile`; confirme em console AWS → IAM → Roles → LabRole → aba
"Instance profile ARNs" e ajuste `instance_profile_name` no `terraform.tfvars`
se divergir. `""` sobe a instância sem profile — o stack funciona e só o backup
para S3 fica de fora, anexável depois sem recriar nada.

## Sequência típica

```bash
infra/scripts/01-empacotar-imagens.sh     # precisa do Docker Desktop aberto
infra/scripts/02-provisionar.sh           # plano, nada é criado
infra/scripts/02-provisionar.sh --apply    # cria a infra
# >>> D-25 AQUI: copie terraform.tfstate e stocksense-key.pem para fora do repo
infra/scripts/03-enviar.sh
infra/scripts/04-subir.sh
infra/scripts/05-fumaca.sh
```

## HTTPS

O `04-subir.sh` sobe em **HTTP puro no IP** (`SITE_ADDRESS=:80`). Isso é
deliberado: o Let's Encrypt **não emite certificado para endereço IP** (§5), e
deixar o TLS fora da primeira subida tira do caminho crítico a propagação de DNS
e o rate limit de 5 falhas/hora do ACME.

Para ganhar o cadeado depois, aponte um nome para o Elastic IP, confirme com
`nslookup` e rode:

```bash
infra/scripts/04-subir.sh stocksense.duckdns.org
```

## Parar a cobrança

A instância é o que custa. O Elastic IP e o EBS continuam correndo (~US$ 6/mês)
mesmo parada — ver §7.1 e §9.8.

```bash
aws ec2 stop-instances  --instance-ids "$INSTANCE_ID"
aws ec2 start-instances --instance-ids "$INSTANCE_ID"   # containers voltam sozinhos
```

No Learner Lab a instância também é parada quando a sessão do lab encerra.
