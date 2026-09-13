#!/usr/bin/env bash
# ============================================================================
# 01 — Empacota as imagens de produção para viajarem até a EC2.
#      Executa a opção (c) do D-17: build AQUI, a t3.medium nunca compila.
#
# Só as DUAS imagens próprias viajam. caddy:2-alpine, nginx:alpine e mysql:8.0
# a instância baixa do Docker Hub em segundos — não faz sentido mandá-las pelo
# seu upload residencial.
#
# Uso:  infra/scripts/01-empacotar-imagens.sh
# ============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$RAIZ"

ENV_BUILD="${ENV_BUILD:-.env.ensaio}"
TARBALL="infra/dist/stocksense-images.tar.gz"

echo "==> Verificando o Docker"
docker info >/dev/null 2>&1 || {
  echo "ERRO: o daemon do Docker não responde. Abra o Docker Desktop e espere" >&2
  echo "      o ícone ficar verde antes de rodar este script." >&2
  exit 1
}

# O compose interpola o arquivo INTEIRO antes de qualquer coisa, e o
# docker-compose.prod.yml usa ${VAR:?} em cinco variáveis. Sem --env-file ele
# aborta já no parse, mesmo que a gente só queira buildar.
[ -f "$ENV_BUILD" ] || {
  echo "ERRO: $ENV_BUILD não existe." >&2
  echo "      É o .env de ensaio do D-03, com DB_ROOT_PASSWORD, DB_USERNAME," >&2
  echo "      DB_PASSWORD, JWT_SECRET e SITE_ADDRESS. Veja o D-03 no tasks.md." >&2
  exit 1
}

echo "==> Buildando backend e ml-service (produção)"
docker compose -f docker-compose.prod.yml --env-file "$ENV_BUILD" build backend ml-service

echo "==> Conferindo o pin do cmdstanpy (D-46) dentro da imagem"
# Sem o pin, o Prophet cai em fallback SILENCIOSO e a T10 fica inválida.
# Melhor descobrir aqui do que na nuvem.
VERSAO_CMDSTANPY="$(docker run --rm --entrypoint pip stocksense-ml:prod show cmdstanpy 2>/dev/null | awk '/^Version:/{print $2}')"
if [ "$VERSAO_CMDSTANPY" = "1.2.4" ]; then
  echo "    cmdstanpy $VERSAO_CMDSTANPY — ok"
else
  echo "    AVISO: cmdstanpy='$VERSAO_CMDSTANPY', esperado 1.2.4 (D-46)." >&2
  echo "           O Prophet pode cair em fallback sem erro visível." >&2
fi

echo "==> Salvando as imagens em $TARBALL"
mkdir -p infra/dist
docker save stocksense-backend:prod stocksense-ml:prod | gzip -c > "$TARBALL"

TAMANHO="$(du -h "$TARBALL" | cut -f1)"
echo
echo "==> Pronto: $TARBALL ($TAMANHO)"
echo "    Medido no D-04: ~385 MB comprimidos. O 03-enviar.sh manda este arquivo."
