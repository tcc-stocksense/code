# S3 — destino do mysqldump diário (§9.7).
# A instance profile do lab autentica a chamada: nenhuma access key no disco da EC2.
# A role NÃO é criada aqui (ver o bloco no fim do arquivo).

# Nome de bucket é global na AWS inteira; o sufixo evita colisão.
resource "random_id" "bucket" {
  byte_length = 4
}

resource "aws_s3_bucket" "backup" {
  bucket = "stocksense-backup-${random_id.bucket.hex}"

  tags = { Name = "stocksense-backup" }
}

resource "aws_s3_bucket_public_access_block" "backup" {
  bucket                  = aws_s3_bucket.backup.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup" {
  bucket = aws_s3_bucket.backup.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backup" {
  bucket = aws_s3_bucket.backup.id

  rule {
    id     = "expira-dumps-antigos"
    status = "Enabled"

    filter {}

    expiration {
      days = var.backup_retention_days
    }
  }
}

# ----------------------------------------------------------------------------
# IAM — NÃO criado aqui. Restrição do AWS Academy Learner Lab.
#
# A versão anterior deste arquivo criava `aws_iam_role` + `aws_iam_role_policy`
# + `aws_iam_instance_profile`, com permissão mínima de `s3:PutObject` só neste
# bucket. No Learner Lab isso falha no apply: a política do lab nega
# iam:CreateRole. O lab fornece uma role pronta (`LabRole`) e a instance
# profile correspondente, que é o que a EC2 passa a usar.
#
# O que se perde: o privilégio mínimo. A LabRole tem permissões amplas, então a
# EC2 pode mais que gravar dumps. É limitação do ambiente, não escolha de
# projeto — registrar no §10.2 do infraestrutura-nuvem.md junto das outras.
# O que se mantém: nenhuma access key em disco. A autenticação continua vindo
# da instance profile, que é o ponto do §9.7.
#
# O nome sai em `var.instance_profile_name` porque varia entre versões do lab.
# Confirmar antes do apply em: console AWS → IAM → Roles → LabRole → aba
# "Instance profile ARNs". Se o nome estiver errado, o apply falha em
# `aws_instance` com "InvalidParameterValue: IAM Instance Profile not found".
# ----------------------------------------------------------------------------
