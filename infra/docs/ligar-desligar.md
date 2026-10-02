# Runbook — ligar e desligar a instância

> Implementa o §9.8 do [`infraestrutura-nuvem.md`](../infraestrutura-nuvem.md) com os
> identificadores reais, e registra a **verificação prática** do §7.2 (D-39).

## Identificadores

| | |
|---|---|
| Instância | `i-01fb1975491b85fb1` (t3.medium, 2 vCPU / 4 GB) |
| Elastic IP | `107.20.236.251` — **não muda** ao desligar |
| Região | `us-east-1` |
| Volume de dados | `stocksense_db_data` (Docker, no EBS da instância) |
| URL | http://107.20.236.251 |

## Por que desligar

A instância é o que consome crédito. Desligada, param CPU e memória; continuam
correndo **o disco EBS (30 GB gp3) e o endereço IPv4**, somando ~US$ 6/mês — a AWS
cobra IPv4 público desde 2024 mesmo com a instância parada.

No **AWS Academy Learner Lab isso acontece sozinho**: a instância é parada quando a
sessão do lab encerra. O estado "parada" é o padrão do ambiente, não algo a lembrar.

## Comandos

Exigem credenciais do lab válidas (elas expiram com a sessão — ver
[`../scripts/README.md`](../scripts/README.md)).

```bash
aws ec2 stop-instances  --instance-ids i-01fb1975491b85fb1
aws ec2 start-instances --instance-ids i-01fb1975491b85fb1
aws ec2 describe-instances --instance-ids i-01fb1975491b85fb1 \
  --query 'Reservations[0].Instances[0].State.Name' --output text
```

Sem o AWS CLI instalado, o mesmo se faz pelo console (EC2 → Instances → Instance state)
ou por `boto3`. Para desligar, serve também `sudo shutdown -h now` por SSH: o
comportamento padrão de shutdown da instância é `stop`, não `terminate`. Mas **religar
exige a API** — SSH não alcança máquina desligada.

## Verificação prática (2026-09-13)

Ciclo completo medido, com comparação do estado antes e depois:

| Etapa | Tempo |
|---|---|
| `stop` → estado `stopped` | 32 s |
| Confirmação de indisponibilidade | conexão recusada ✓ |
| `start` → estado `running` | 11 s |
| SSH respondendo | 11 s depois |
| Containers no ar | **automático, sem nenhum comando** |
| HTTP 200 pela borda | imediato |

**Indisponibilidade total: pouco menos de 1 minuto.**

Confirmado o que o §7.2 afirma:

1. **Os containers voltam sozinhos.** O `user_data` deixa o Docker com
   `systemctl enable`, e os cinco serviços estão como `restart: unless-stopped` no
   `docker-compose.prod.yml`. Não é preciso rodar `up` nem entrar na máquina.
2. **O banco não perde dados.** Antes e depois: os mesmos 12 produtos, mesmos ids, mesmo
   líder da Curva ABC (Achocolatado em Pó 400g, R$ 62.953,13) e mesmos estoque e classe
   produto a produto. A comparação foi campo a campo, não só de contagem.
3. **O endereço não muda.** O Elastic IP voltou idêntico, então links e DNS continuam
   válidos.

## O que NÃO sobrevive

| Ação | Dados | Elastic IP |
|---|---|---|
| `stop` / `start` | ✅ preservados | ✅ o mesmo |
| Reinício do SO | ✅ preservados | ✅ o mesmo |
| `docker compose down` **sem** `-v` | ✅ preservados | ✅ o mesmo |
| `docker compose down -v` | ❌ **apagados** | ✅ o mesmo |
| `terraform destroy` | ❌ **apagados** | ❌ **outro IP** |

Para zerar só o banco sem tocar na AWS — útil para recomeçar de um estado limpo:

```bash
cd /home/ubuntu/stocksense
docker compose -f docker-compose.prod.yml --env-file .env down -v
docker compose -f docker-compose.prod.yml --env-file .env up -d --no-build
```

O Flyway recria o schema e o seed da `V2` (estabelecimento e fornecedor padrão), e o
catálogo volta vazio. Depois, `infra/scripts/05-fumaca.sh` repovoa com os 10 produtos.

⚠️ **O `05-fumaca.sh` só serve para banco limpo.** Rodá-lo sobre um banco que já tem
esses dados faria upsert dos produtos (inofensivo) mas **acrescentaria 1.690 linhas de
vendas duplicadas**, porque a importação de vendas não deduplica.

## Antes da defesa

Tirar um **snapshot do EBS** com o sistema carregado e validado (D-40): restaura a
máquina inteira, não só o banco.
