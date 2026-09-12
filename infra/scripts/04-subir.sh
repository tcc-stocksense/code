#!/usr/bin/env bash
# ============================================================================
# 04 — Sobe o stack na EC2: D-29 (.env de produção) + D-31 (up + healthchecks).
#
# SITE_ADDRESS=:80 por padrão — HTTP puro no IP, o modo documentado no
# Caddyfile:18. O Let's Encrypt NÃO emite certificado para endereço IP, então
# HTTPS é um passo posterior e não deste script: quando houver um nome
# apontando para o Elastic IP, rode
#
#     infra/scripts/04-subir.sh stocksense.duckdns.org
#
# que troca o SITE_ADDRESS e reinicia o Caddy. O volume caddy_data persiste os
# certificados — sem ele, cada subida pediria emissão nova e queimaria a cota
# do Let's Encrypt (5 falhas/hora por hostname).
# ============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$RAIZ/infra/scripts/.outputs.env"

SITE="${1:-:80}"
DESTINO="/home/ubuntu/stocksense"
SSH_OPTS=(-i "$PEM" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10)
ALVO="ubuntu@$IP_PUBLICO"
chmod 600 "$PEM" 2>/dev/null || true

echo "==> D-29: .env de produção na VM (SITE_ADDRESS=$SITE)"
ssh "${SSH_OPTS[@]}" "$ALVO" SITE="$SITE" DESTINO="$DESTINO" bash -s <<'REMOTO'
set -euo pipefail
cd "$DESTINO"

if [ -f .env ]; then
  # NÃO regerar. O MySQL só aplica MYSQL_USER/MYSQL_PASSWORD na PRIMEIRA
  # inicialização do volume (lição do D-04): trocar a senha agora faria o
  # backend falhar a autenticação por um motivo que não aparece em log nenhum.
  echo "    .env já existe — preservado. Só o SITE_ADDRESS é atualizado."
  if grep -q '^SITE_ADDRESS=' .env; then
    sed -i "s|^SITE_ADDRESS=.*|SITE_ADDRESS=$SITE|" .env
  else
    echo "SITE_ADDRESS=$SITE" >> .env
  fi
else
  echo "    criando .env com segredos novos (nunca os do ensaio local)"
  umask 077
  cat > .env <<EOF
# Gerado na instância por 04-subir.sh — nunca versionado, nunca reaproveitado.
DB_ROOT_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
DB_USERNAME=appuser
DB_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
JWT_SECRET=$(openssl rand -base64 48 | tr -d '/+=' | head -c 64)
SITE_ADDRESS=$SITE
EOF
fi
chmod 600 .env
echo "    permissões: $(stat -c '%a %n' .env)"
REMOTO

echo "==> D-31: subindo (--no-build: as imagens vieram do 03)"
ssh "${SSH_OPTS[@]}" "$ALVO" \
  "cd $DESTINO && docker compose -f docker-compose.prod.yml --env-file .env up -d --no-build"

echo "==> Esperando os healthchecks (start_period do backend é 90s)"
ssh "${SSH_OPTS[@]}" "$ALVO" DESTINO="$DESTINO" bash -s <<'REMOTO'
set -uo pipefail
cd "$DESTINO"
for i in $(seq 1 40); do
  PENDENTES="$(docker compose -f docker-compose.prod.yml ps --format '{{.Name}} {{.Status}}' \
              | grep -E 'starting|unhealthy' || true)"
  [ -z "$PENDENTES" ] && break
  sleep 15
done
echo
docker compose -f docker-compose.prod.yml ps --format '    {{.Name}}\t{{.Status}}'
echo
echo "    Healthchecks por dentro (§9.6):"
docker exec stocksense-backend wget -qO- http://localhost:8080/actuator/health && echo "  <- backend"
docker exec stocksense-backend wget -qO- http://ml-service:8000/health      && echo "  <- ml-service via rede interna"
echo
echo "    R6 — nenhum serviço interno publica porta:"
for c in stocksense-db stocksense-ml stocksense-backend; do
  echo "      $c: '$(docker port $c)'"
done
REMOTO

echo
echo "==> Fumaça mínima pela borda"
CODIGO="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "http://$IP_PUBLICO/" || true)"
echo "    GET http://$IP_PUBLICO/  ->  $CODIGO  (esperado 200)"
echo
echo "    Abra:  http://$IP_PUBLICO"
echo "    Próximo: infra/scripts/05-fumaca.sh"
