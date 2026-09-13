#!/usr/bin/env bash
# ============================================================================
# 02 — Provisiona a AWS: D-21 (tfvars), D-22 (plan revisado), D-24 (apply).
#
# Por padrão SÓ FAZ O PLANO e roda as conferências que o D-22 exige. Aplicar é
# um segundo comando, explícito:
#
#     infra/scripts/02-provisionar.sh            # plan + conferências
#     infra/scripts/02-provisionar.sh --apply    # aplica o plano já revisado
#
# AWS ACADEMY LEARNER LAB. As credenciais do lab são TEMPORÁRIAS (expiram em
# ~3-4h) e incluem um terceiro campo, AWS_SESSION_TOKEN. Pegue-as em
# "AWS Details" → "AWS CLI" no lab e cole em  infra/lab-credentials.env
# (gitignorado) neste formato:
#
#     AWS_ACCESS_KEY_ID=ASIA...
#     AWS_SECRET_ACCESS_KEY=...
#     AWS_SESSION_TOKEN=...
#
# Se o lab tiver sido reiniciado, as credenciais mudam: recole o bloco.
# ============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TF="$RAIZ/infra/terraform"
CREDS="$RAIZ/infra/lab-credentials.env"
SAIDA="$RAIZ/infra/scripts/.outputs.env"
PLANO="$TF/plano.tfplan"

APLICAR=0
[ "${1:-}" = "--apply" ] && APLICAR=1

# ---------------------------------------------------------------- credenciais
if [ -f "$CREDS" ]; then
  echo "==> Carregando credenciais de infra/lab-credentials.env"
  # Aceita com ou sem 'export', e ignora comentários e o [default] do formato INI.
  while IFS= read -r linha; do
    linha="${linha%$'\r'}"   # colagem vinda do Windows traz CR e quebraria o token
    linha="${linha#export }"
    case "$linha" in
      \#*|\[*|'') continue ;;
      AWS_ACCESS_KEY_ID=*|AWS_SECRET_ACCESS_KEY=*|AWS_SESSION_TOKEN=*) export "${linha?}" ;;
      aws_access_key_id=*)     export AWS_ACCESS_KEY_ID="${linha#*=}" ;;
      aws_secret_access_key=*) export AWS_SECRET_ACCESS_KEY="${linha#*=}" ;;
      aws_session_token=*)     export AWS_SESSION_TOKEN="${linha#*=}" ;;
    esac
  done < "$CREDS"
fi

FALTA=""
[ -z "${AWS_ACCESS_KEY_ID:-}" ]     && FALTA="$FALTA AWS_ACCESS_KEY_ID"
[ -z "${AWS_SECRET_ACCESS_KEY:-}" ] && FALTA="$FALTA AWS_SECRET_ACCESS_KEY"
[ -z "${AWS_SESSION_TOKEN:-}" ]     && FALTA="$FALTA AWS_SESSION_TOKEN"
if [ -n "$FALTA" ]; then
  echo "ERRO: faltam credenciais:$FALTA" >&2
  echo "      No Learner Lab as três são obrigatórias — o SESSION_TOKEN também." >&2
  echo "      Cole o bloco de 'AWS Details' → 'AWS CLI' em $CREDS" >&2
  exit 1
fi
echo "    Credenciais presentes (chave ${AWS_ACCESS_KEY_ID:0:6}…). Lembre: expiram com a sessão do lab."

# ------------------------------------------------------------------ D-21 tfvars
cd "$TF"
echo "==> D-21: descobrindo seu IP público"
IP="$(curl -s --max-time 10 https://checkip.amazonaws.com | tr -d '[:space:]')"
[ -n "$IP" ] || { echo "ERRO: não consegui descobrir seu IP público." >&2; exit 1; }
echo "    $IP/32 — único autorizado a abrir SSH"

if [ -f terraform.tfvars ]; then
  # IP residencial muda; atualiza só essa linha e preserva o resto do arquivo.
  if grep -q '^dev_ip' terraform.tfvars; then
    sed -i "s|^dev_ip.*|dev_ip = \"$IP/32\"|" terraform.tfvars
    echo "    terraform.tfvars: dev_ip atualizado"
  else
    echo "dev_ip = \"$IP/32\"" >> terraform.tfvars
  fi
else
  cat > terraform.tfvars <<EOF
# Gerado por infra/scripts/02-provisionar.sh — não versionado.
dev_ip = "$IP/32"

# AWS Academy Learner Lab: a role não pode ser criada (iam:CreateRole negado).
# Usa-se a instance profile que o lab já fornece. Confirme o nome em
# console AWS → IAM → Roles → LabRole → "Instance profile ARNs".
# Use "" para subir sem profile: o stack funciona e só o backup p/ S3 fica fora.
instance_profile_name = "LabInstanceProfile"
EOF
  echo "    terraform.tfvars criado"
fi

# -------------------------------------------------------------------- D-22 plan
echo "==> terraform init"
terraform init -input=false >/dev/null

echo "==> D-22: gerando o plano"
terraform plan -input=false -out="$PLANO"

echo
echo "==> Conferências obrigatórias do D-22"
TEXTO="$(terraform show -no-color "$PLANO")"
ERROS=0

if echo "$TEXTO" | grep -q 'aws_nat_gateway'; then
  echo "    ✗ NAT Gateway no plano — ~US\$ 32/mês, um terço do crédito (§4.2)"; ERROS=1
else
  echo "    ✓ nenhum NAT Gateway"
fi

N_EIP="$(echo "$TEXTO" | grep -c 'resource "aws_eip"' || true)"
if [ "$N_EIP" = "1" ]; then echo "    ✓ exatamente 1 Elastic IP"
else echo "    ✗ $N_EIP Elastic IPs (esperado 1)"; ERROS=1; fi

if echo "$TEXTO" | grep -E 'from_port' | grep -qE '\b(8080|8000|3306)\b'; then
  echo "    ✗ o SG abre 8080/8000/3306 — esses serviços não podem ter porta pública (R6)"; ERROS=1
else
  echo "    ✓ SG sem 8080/8000/3306"
fi

if echo "$TEXTO" | grep -q 'aws_iam_role'; then
  echo "    ✗ o plano cria role IAM — o Learner Lab nega iam:CreateRole"; ERROS=1
else
  echo "    ✓ nenhuma role IAM criada (usa a do lab)"
fi

echo "    — instance_type: $(echo "$TEXTO" | grep -m1 'instance_type' | sed 's/.*= *//')"
echo "    — recursos a criar: $(echo "$TEXTO" | grep -c '^  # .* will be created' || true)"

if [ "$ERROS" -ne 0 ]; then
  echo; echo "ERRO: o plano não passou nas conferências do D-22. Não aplique." >&2
  exit 1
fi

if [ "$APLICAR" -eq 0 ]; then
  echo
  echo "==> Plano pronto e conferido, NADA foi criado ainda."
  echo "    Leia o plano acima. Para aplicar:  infra/scripts/02-provisionar.sh --apply"
  exit 0
fi

# ------------------------------------------------------------------- D-24 apply
echo
echo "==> D-24: aplicando"
terraform apply -input=false "$PLANO"

echo "==> Gravando os outputs em infra/scripts/.outputs.env"
{
  echo "# Gerado por 02-provisionar.sh em $(date '+%Y-%m-%d %H:%M:%S')"
  echo "IP_PUBLICO=$(terraform output -raw ip_publico)"
  echo "INSTANCE_ID=$(terraform output -raw instance_id)"
  # O bucket saiu do Terraform (SCP do lab — ver backup.tf). Quem o cria e o
  # nomeia e o backup.sh, a partir do id da conta.
  echo "PEM=$TF/stocksense-key.pem"
} > "$SAIDA"
cat "$SAIDA"

echo
terraform output -raw proximos_passos
echo
echo "⚠️  D-25 AGORA, antes de qualquer outra coisa: copie terraform.tfstate e"
echo "    stocksense-key.pem para fora do repositório. O state guarda a chave SSH"
echo "    privada em texto claro; perder a pasta = perder o acesso e o destroy limpo."
