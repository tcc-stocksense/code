# S3 + IAM — destino do mysqldump diário (§9.7).
# A instance profile autentica a chamada: nenhuma access key no disco da EC2.

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

resource "aws_iam_role" "ec2" {
  name = "stocksense-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

# Permissão mínima: gravar objetos, e só neste bucket.
resource "aws_iam_role_policy" "backup_write" {
  name = "stocksense-s3-backup-write"
  role = aws_iam_role.ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "${aws_s3_bucket.backup.arn}/*"
    }]
  })
}

resource "aws_iam_instance_profile" "ec2" {
  name = "stocksense-ec2-profile"
  role = aws_iam_role.ec2.name
}
