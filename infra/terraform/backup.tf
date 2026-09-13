# ----------------------------------------------------------------------------
# Backup (§9.7) — o S3 NÃO é gerenciado por Terraform. Restrição do ambiente.
#
# POR QUE ESTE ARQUIVO ESTÁ VAZIO DE RECURSOS
#
# A versão anterior criava o bucket, o bloqueio de acesso público, a criptografia
# e o lifecycle de 30 dias, mais uma role IAM com permissão mínima de
# `s3:PutObject`. Nada disso sobrevive ao AWS Academy Learner Lab:
#
#   1. `iam:CreateRole` é negado → usa-se a `LabRole` pronta do lab, referenciada
#      em `var.instance_profile_name` e aplicada em compute.tf.
#
#   2. `s3:GetBucketObjectLockConfiguration` é negado por uma service control
#      policy da organização (p-gi77lu0b). O provider AWS chama essa API ao LER
#      qualquer `aws_s3_bucket` — no create e em todo refresh posterior. Efeito
#      medido em 2026-09-13: o apply criou o bucket e abortou logo depois, e a
#      partir dali até `terraform plan` passou a falhar, porque o refresh do
#      recurso existente bate na mesma API.
#
#      Não há como contornar: não existe flag no provider para pular essa
#      leitura, e o erro é de autorização, não de configuração.
#
# COMO O BUCKET PASSA A EXISTIR
#
# O `infra/scripts/backup.sh` o cria na primeira execução, se não existir, usando
# o AWS CLI da instância autenticado pela instance profile. O nome é derivado do
# id da conta (`stocksense-backup-<account-id>`): globalmente único, determinístico
# e sem precisar de estado.
#
# O QUE SE PERDE
#
# Privilégio mínimo (a LabRole é ampla) e o lifecycle que expiraria dumps com
# mais de 30 dias — eles se acumulam até alguém apagar. Bloqueio de acesso
# público e criptografia SSE-S3 continuam valendo: a AWS os aplica por padrão em
# buckets novos desde 2023. Registrar as duas perdas no §10.2 como limitações do
# ambiente, não como escolha de projeto.
#
# Se um dia a conta deixar de ser Learner Lab, o histórico deste arquivo tem a
# versão completa — `git log -- infra/terraform/backup.tf`.
# ----------------------------------------------------------------------------
