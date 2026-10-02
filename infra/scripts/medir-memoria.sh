#!/usr/bin/env bash
# ============================================================================
# medir-memoria.sh — amostra o uso de memória dos containers ao longo do tempo.
#
# Serve o D-07 (pico sob carga na máquina local) e o D-43 (o mesmo na t3.medium).
# Um `docker stats --no-stream` solto dá o instante em que você olhou, que é
# justamente o número que não interessa: o que importa é o PICO durante o lote
# do motor, e ele dura minutos.
#
#   ./medir-memoria.sh amostras.csv           # amostra até Ctrl-C (ou kill)
#   ./medir-memoria.sh --resumo amostras.csv  # pico e média por container
#
# Típico:
#   ./medir-memoria.sh /tmp/m.csv & PID=$!
#   ./05-fumaca.sh http://localhost
#   kill $PID; ./medir-memoria.sh --resumo /tmp/m.csv
# ============================================================================
set -uo pipefail

INTERVALO="${INTERVALO:-5}"
CONTAINERS="${CONTAINERS:-stocksense-db stocksense-backend stocksense-ml stocksense-caddy stocksense-frontend}"

resumo() {
  local csv="$1"
  [ -f "$csv" ] || { echo "ERRO: $csv não existe" >&2; exit 1; }
  echo "Amostras: $(( $(wc -l < "$csv") - 1 ))  ·  intervalo ${INTERVALO}s"
  echo
  printf '%-22s %12s %12s %12s\n' "CONTAINER" "PICO(MiB)" "MEDIA(MiB)" "LIMITE(MiB)"
  # campos: epoch,container,usado_mib,limite_mib
  awk -F, 'NR>1 && $3!="" {
      s[$2]+=$3; n[$2]++; if ($3+0 > p[$2]+0) p[$2]=$3; lim[$2]=$4
    }
    END { for (c in n) printf "%-22s %12.1f %12.1f %12s\n", c, p[c], s[c]/n[c], lim[c] }' "$csv" | sort
  echo
  awk -F, 'NR>1 && $3!="" { t[$1]+=$3 } END {
      for (e in t) if (t[e]+0 > max+0) { max=t[e] }
      printf "Pico SOMADO de todos os containers: %.0f MiB (%.2f GiB)\n", max, max/1024
    }' "$csv"
  echo "Orçamento do §6.1: 3,9 GB dos 4 GB da t3.medium."
}

if [ "${1:-}" = "--resumo" ]; then resumo "${2:?passe o csv}"; exit 0; fi

CSV="${1:?uso: medir-memoria.sh <arquivo.csv> | --resumo <arquivo.csv>}"
echo "epoch,container,usado_mib,limite_mib" > "$CSV"
echo "Amostrando a cada ${INTERVALO}s em $CSV — pare com Ctrl-C." >&2

# Converte "454.5MiB / 600MiB" em duas colunas numéricas em MiB.
paraMib() {
  awk '{
    v=$1; sub(/[A-Za-z]+$/,"",v); u=$1; sub(/^[0-9.]+/,"",u)
    if (u=="GiB"||u=="GB") v=v*1024; else if (u=="KiB"||u=="kB") v=v/1024
    printf "%.1f", v
  }' <<<"$1"
}

while :; do
  AGORA=$(date +%s)
  # Uma chamada só para todos os containers: menos overhead que N chamadas.
  while IFS='|' read -r NOME USO; do
    [ -z "$NOME" ] && continue
    USADO="${USO%%/*}"; LIMITE="${USO##*/}"
    echo "$AGORA,$NOME,$(paraMib "$(tr -d ' ' <<<"$USADO")"),$(paraMib "$(tr -d ' ' <<<"$LIMITE")")" >> "$CSV"
  done < <(docker stats --no-stream --format '{{.Name}}|{{.MemUsage}}' $CONTAINERS 2>/dev/null)
  sleep "$INTERVALO"
done
