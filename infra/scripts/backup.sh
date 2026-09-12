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
#     sudo tee /etc/stocksense-backup.conf <<<'BUCKET=stocksense-backup-xxxxxxxx'
#
# O nome do bucket tem sufixo aleatório (random_id no backup.tf) — sai no output
# 'bucket_backup' do terraform e é lido daqui via /etc/stocksense-backup.conf.
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
: "${BUCKET:?defina BUCKET em $CONF (output bucket_backup do terraform)}"

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
