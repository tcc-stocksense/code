#!/usr/bin/env bash
# ============================================================================
# 05 — Fumaça pela API (D-33). Valida a trilha A inteira sem abrir o navegador.
#
# Serve para os dois ambientes:
#     infra/scripts/05-fumaca.sh http://localhost    # ensaio local (D-07/D-04)
#     infra/scripts/05-fumaca.sh                     # produção, IP do .outputs.env
#
# Cronometra o POST /api/motor/recalcular, que é o número do D-35 e vai para a
# metodologia do TCC (o D-41 mediu 0,42-0,53 s/produto em desktop de 12 CPUs,
# fora do Docker — aqui é a t3.medium de verdade).
# ============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ -n "${1:-}" ]; then
  BASE="$1"
else
  source "$RAIZ/infra/scripts/.outputs.env"
  BASE="http://$IP_PUBLICO"
fi
API="$BASE/api"

EMAIL="${EMAIL:-admin@stocksense.local}"
SENHA="${SENHA:-admin123}"
FIXTURES="$RAIZ/ml-service/app/tests/fixtures"
PYTHON="$RAIZ/ml-service/venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON="$RAIZ/ml-service/venv/bin/python"

echo "==> Alvo: $BASE"

# ------------------------------------------------------------------- planilhas
# 5_vendas.xlsx é gerada com 180 dias TERMINANDO ONTEM. Se for antiga, o
# histórico chega velho e os dias-até-ruptura saem deslocados. Regerar é barato.
echo "==> Planilhas de importação"
if [ -x "$PYTHON" ]; then
  (cd "$RAIZ/ml-service" && "$PYTHON" app/tests/generate_synthetic_data.py >/dev/null 2>&1) \
    && echo "    regeradas (janela terminando ontem)" \
    || echo "    AVISO: o gerador falhou; usando as planilhas que já existem."
else
  echo "    AVISO: venv do ml-service não encontrado; usando as planilhas existentes."
fi
for f in 2_produtos.xlsx 5_vendas.xlsx; do
  [ -f "$FIXTURES/$f" ] || { echo "ERRO: falta $FIXTURES/$f" >&2; exit 1; }
  echo "    $f  $(du -h "$FIXTURES/$f" | cut -f1)"
done

json() { grep -o "\"$2\":[^,}]*" <<<"$1" | head -1 | sed 's/.*://; s/"//g'; }

# ----------------------------------------------------------------------- login
echo "==> POST /api/auth/login"
RESP="$(curl -s -X POST "$API/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"senha\":\"$SENHA\"}")"
TOKEN="$(json "$RESP" token)"
[ -n "$TOKEN" ] || { echo "ERRO: login falhou. Resposta: $RESP" >&2; exit 1; }
echo "    ok — estabelecimento '$(json "$RESP" nomeFantasia)'"
AUTH=(-H "Authorization: Bearer $TOKEN")

# ------------------------------------------------------------------ importação
for par in "produtos:2_produtos.xlsx" "vendas:5_vendas.xlsx"; do
  ROTA="${par%%:*}"; ARQ="${par##*:}"
  echo "==> POST /api/importacao/$ROTA  ($ARQ)"
  R="$(curl -s -X POST "$API/importacao/$ROTA" "${AUTH[@]}" -F "arquivo=@$FIXTURES/$ARQ")"
  echo "    $R" | head -c 300; echo
done

# ----------------------------------------------------------------------- motor
echo "==> POST /api/motor/recalcular — D-35, cronometrando"
INICIO=$(date +%s)
R="$(curl -s -X POST "$API/motor/recalcular" "${AUTH[@]}" --max-time 3600)"
FIM=$(date +%s)
SEG=$((FIM - INICIO))
echo "    $R" | head -c 400; echo
echo "    ⏱  ${SEG}s  ($((SEG / 60))min $((SEG % 60))s)  <- número do D-35"

# ------------------------------------------------------------------------- KPIs
echo "==> Conferindo as telas pela API"
for rota in /dashboard /alertas /curva-abc /produtos; do
  CODIGO="$(curl -s -o /dev/null -w '%{http_code}' "$API$rota" "${AUTH[@]}")"
  printf '    %-14s %s\n' "$rota" "$CODIGO"
done

PROD="$(curl -s "$API/produtos" "${AUTH[@]}")"
ID="$(grep -o '"id":[0-9]*' <<<"$PROD" | head -1 | sed 's/.*://')"
if [ -n "$ID" ]; then
  for rota in "/produtos/$ID/detalhe" "/produtos/$ID/metricas"; do
    CODIGO="$(curl -s -o /dev/null -w '%{http_code}' "$API$rota" "${AUTH[@]}")"
    printf '    %-24s %s\n' "$rota" "$CODIGO"
  done
  echo "==> Métricas do produto $ID (T10 — HW x Prophet):"
  curl -s "$API/produtos/$ID/metricas" "${AUTH[@]}" | head -c 600; echo
fi

echo
echo "==> Fumaça concluída. Agora o D-34: o mesmo roteiro pelo navegador em $BASE"
