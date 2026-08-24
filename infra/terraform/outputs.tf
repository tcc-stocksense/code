output "ip_publico" {
  description = "Elastic IP. É este valor que vai no DuckDNS (Parte 5)."
  value       = aws_eip.app.public_ip
}

output "comando_ssh" {
  description = "Copie e cole para entrar na instância."
  value       = "ssh -i stocksense-key.pem ubuntu@${aws_eip.app.public_ip}"
}

output "bucket_backup" {
  description = "Nome do bucket S3 — usar no script de backup do §9.7."
  value       = aws_s3_bucket.backup.id
}

output "instance_id" {
  description = "Para ligar/desligar e economizar crédito (§9.8)."
  value       = aws_instance.app.id
}

output "proximos_passos" {
  value = <<-EOT

    1. DuckDNS: aponte stocksense.duckdns.org para ${aws_eip.app.public_ip}
    2. Aguarde ~3 min o bootstrap (Docker + swap) terminar
    3. ssh -i stocksense-key.pem ubuntu@${aws_eip.app.public_ip}
    4. Confirme: ls /var/log/stocksense-bootstrap-done && free -h
    5. Siga o §9.2 em diante: git clone, build, .env, docker compose up

  EOT
}
