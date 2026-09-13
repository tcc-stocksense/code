#!/usr/bin/env bash
# ============================================================================
# backup.sh — D-36. Roda NA INSTÂNCIA, não na sua máquina.
#
# mysqldump (de dentro do container) → gzip → S3. A instance profile autentica:
# nenhuma access key em disco, que é o ponto do §9.7.
#
# Instalação (D-37):
#     sudo cp /home/ubuntu/stocksense/infra/scripts/backup.sh /etc/cron.daily/stocksense-backup
#     sudo chmod +x /etc/cron.daily/stocksense-backup
#
# O bucket NÃO precisa ser configurado: o script deriva o nome do id da conta
# (stocksense-backup-<account-id>) e o cria na primeira execução. Para usar outro
# nome, crie /etc/stocksense-backup.conf com 'BUCKET=meu-bucket'.
#
# Isso mudou em 2026-09-13: o bucket saía do Terraform, mas a SCP do Learner Lab
# nega s3:GetBucketObjectLockConfiguration, que o provider chama ao ler qualquer
# aws_s3_bucket — o que fazia até o `terraform plan` falhar. Ver backup.tf.
#
# Em cron não existe PATH decente nem variáveis de ambiente da sua sessão: tudo
# o que o script precisa ele resolve por caminho absoluto ou lê do disco.
# ============================================================================
set -euo pipefail

RAIZ="${STOCKSENSE_RAIZ:-/home/ubuntu/stocksense}"
COMPOSE="$RAIZ/docker-compose.prod.yml"
CONF="${STOCKSENSE_BACKUP_CONF:-/etc/stocksense-backup.conf}"
AWS="$(command -v aws || echo /usr/local/bin/aws)"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

[ -f "$CONF" ] && . "$CONF"

# O bucket NÃO vem mais do Terraform: a SCP do Learner Lab nega
# s3:GetBucketObjectLockConfiguration, que o provider AWS chama ao ler qualquer
# aws_s3_bucket — o que fazia até o `terraform plan` falhar. Ver backup.tf.
#
# Nome derivado do id da conta quando não informado: globalmente único (ids de
# conta são únicos), determinístico e sem depender de estado — sobrevive a um
# destroy/recriar da infraestrutura.
if [ -z "${BUCKET:-}" ]; then
  CONTA="$("$AWS" sts get-caller-identity --query Account --output text)"
  [ -n "$CONTA" ] || { log "ERRO: nao consegui descobrir o id da conta"; exit 1; }
  BUCKET="stocksense-backup-$CONTA"
  log "BUCKET nao definido em $CONF; usando $BUCKET"
fi

# Cria na primeira execução. head-bucket devolve != 0 quando não existe.
if ! "$AWS" s3api head-bucket --bucket "$BUCKET" >/dev/null 2>&1; then
  log "Bucket $BUCKET nao existe — criando"
  # us-east-1 é a única região que NÃO aceita LocationConstraint no create.
  "$AWS" s3api create-bucket --bucket "$BUCKET" >/dev/null
  log "Bucket criado. Bloqueio de acesso publico e SSE-S3 vem por padrao da AWS."
  log "AVISO: sem lifecycle — dumps antigos se acumulam ate serem apagados a mao."
fi

# A senha do root vive só no .env da instância, com chmod 600.
[ -f "$RAIZ/.env" ] || { log "ERRO: $RAIZ/.env não existe"; exit 1; }
DB_ROOT_PASSWORD="$(grep -E '^DB_ROOT_PASSWORD=' "$RAIZ/.env" | cut -d= -f2-)"
: "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD ausente no .env}"

DATA="$(date +%F)"
DUMP="$(mktemp /tmp/stocksense-XXXXXX.sql.gz)"
trap 'rm -f "$DUMP"' EXIT

log "Gerando o dump de 'stocksense'"
# -T: sem TTY, obrigatório fora de terminal interativo (cron).
# --single-transaction: dump consistente sem travar escrita (InnoDB).
docker compose -f "$COMPOSE" exec -T db \
  mysqldump -u root -p"$DB_ROOT_PASSWORD" --single-transaction --quick stocksense \
  | gzip -c > "$DUMP"

TAMANHO="$(stat -c %s "$DUMP")"
# Um gzip válido e não-vazio passa dos 100 bytes com folga; menos que isso é
# dump vazio por falha de autenticação, que o pipe esconderia.
if [ "$TAMANHO" -lt 100 ]; then
  log "ERRO: dump com $TAMANHO bytes — provável falha de autenticação no MySQL"
  exit 1
fi
log "Dump: $TAMANHO bytes"

DESTINO="s3://$BUCKET/$DATA.sql.gz"
log "Enviando para $DESTINO"
"$AWS" s3 cp "$DUMP" "$DESTINO" --only-show-errors

log "Confirmando o objeto no S3"
"$AWS" s3 ls "$DESTINO" || { log "ERRO: o objeto não apareceu no bucket"; exit 1; }

log "Backup concluído"
