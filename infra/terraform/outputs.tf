output "ip_publico" {
  description = "Elastic IP. É este valor que vai no DuckDNS (Parte 5)."
  value       = aws_eip.app.public_ip
}

output "comando_ssh" {
  description = "Copie e cole para entrar na instância."
  value       = "ssh -i stocksense-key.pem ubuntu@${aws_eip.app.public_ip}"
}

# O bucket de backup saiu do Terraform — ver o comentário em backup.tf. Quem o
# cria é o infra/scripts/backup.sh, na primeira execução, com nome derivado do
# id da conta. Não há output a expor aqui.

output "instance_id" {
  description = "Para ligar/desligar e economizar crédito (§9.8)."
  value       = aws_instance.app.id
}

output "proximos_passos" {
  value = <<-EOT

    1. Aguarde ~3 min o bootstrap (Docker + swap) terminar
    2. ssh -i stocksense-key.pem ubuntu@${aws_eip.app.public_ip}
    3. Confirme: ls /var/log/stocksense-bootstrap-done && free -h
    4. Da sua máquina: infra/scripts/03-enviar.sh e depois 04-subir.sh
    5. Abra http://${aws_eip.app.public_ip} — SITE_ADDRESS=:80, HTTP puro

    HTTPS não sai deste apply: o Let's Encrypt não emite certificado para
    endereço IP (§5). Quando quiser o cadeado, aponte um nome (DuckDNS) para
    ${aws_eip.app.public_ip}, troque SITE_ADDRESS no .env da VM e reinicie
    o Caddy — não precisa recriar nada aqui.

  EOT
}
