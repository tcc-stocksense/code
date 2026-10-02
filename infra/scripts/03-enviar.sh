#!/usr/bin/env bash
# ============================================================================
# 03 — Leva código e imagens para a EC2 (D-27 + D-28, opção (c) do D-17).
#
# Dois eixos, como o D-17 separou:
#   (1) imagens  → docker save (já feito no 01) + scp + docker load
#   (2) arquivos → git clone na VM, porque o compose de produção usa bind mount
#                  para ./Caddyfile e ./frontend/web. Redeploy do front depois
#                  é só 'git pull', sem rebuild.
#
# O repositório é PÚBLICO, então o clone não precisa de deploy key.
#
# Uso:  infra/scripts/03-enviar.sh
# ============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$RAIZ/infra/scripts/.outputs.env"

BRANCH="${BRANCH:-chore/infra-terraform-aws}"
REPO="${REPO:-https://github.com/tcc-stocksense/code.git}"
TARBALL="$RAIZ/infra/dist/stocksense-images.tar.gz"
DESTINO="/home/ubuntu/stocksense"
SSH_OPTS=(-i "$PEM" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10)
ALVO="ubuntu@$IP_PUBLICO"

[ -f "$TARBALL" ] || { echo "ERRO: $TARBALL não existe. Rode o 01-empacotar-imagens.sh primeiro." >&2; exit 1; }
chmod 600 "$PEM" 2>/dev/null || true

echo "==> Esperando o SSH responder em $IP_PUBLICO"
for i in $(seq 1 30); do
  if ssh "${SSH_OPTS[@]}" "$ALVO" true 2>/dev/null; then echo "    conectou"; break; fi
  [ "$i" = "30" ] && { echo "ERRO: SSH não respondeu em 5 min." >&2; exit 1; }
  sleep 10
done

echo "==> D-27: conferindo o bootstrap do user_data"
ssh "${SSH_OPTS[@]}" "$ALVO" bash -s <<'REMOTO'
set -e
if [ -f /var/log/stocksense-bootstrap-done ]; then
  echo "    ✓ sentinela presente"
else
  echo "    ✗ /var/log/stocksense-bootstrap-done NÃO existe — o user_data falhou."
  echo "      Últimas linhas de /var/log/cloud-init-output.log:"
  sudo tail -20 /var/log/cloud-init-output.log || true
  exit 1
fi
echo "    docker:  $(docker --version)"
echo "    compose: $(docker compose version --short)"
echo "    swap:    $(free -h | awk '/Swap:/{print $2}')"
REMOTO

echo "==> Eixo (2): repositório na VM (branch $BRANCH)"
ssh "${SSH_OPTS[@]}" "$ALVO" \
  "if [ -d $DESTINO/.git ]; then \
     cd $DESTINO && git fetch origin $BRANCH && git checkout $BRANCH && git reset --hard origin/$BRANCH; \
   else \
     git clone --branch $BRANCH --single-branch $REPO $DESTINO; \
   fi && cd $DESTINO && git log --oneline -1"

echo "==> Eixo (1): enviando as imagens ($(du -h "$TARBALL" | cut -f1))"
echo "    Este é o passo mais demorado — depende do seu upload."
scp "${SSH_OPTS[@]}" "$TARBALL" "$ALVO:$DESTINO/stocksense-images.tar.gz"

echo "==> docker load na instância"
ssh "${SSH_OPTS[@]}" "$ALVO" \
  "gunzip -c $DESTINO/stocksense-images.tar.gz | docker load && rm -f $DESTINO/stocksense-images.tar.gz && docker images --filter reference='stocksense-*:prod' --format '    {{.Repository}}:{{.Tag}}  {{.Size}}'"

echo
echo "==> Pronto. A t3.medium não compilou nada — era o ponto do D-17."
echo "    Próximo: infra/scripts/04-subir.sh"
