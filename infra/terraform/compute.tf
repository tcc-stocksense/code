# Ubuntu 24.04 LTS oficial da Canonical, sempre a AMI mais recente da região.
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd*/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Key pair gerado pelo próprio Terraform e gravado como stocksense-key.pem.
# Evita o passo manual de criar par de chaves no console.
resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "main" {
  key_name   = "stocksense-key"
  public_key = tls_private_key.ssh.public_key_openssh
}

resource "local_sensitive_file" "pem" {
  filename        = "${path.module}/stocksense-key.pem"
  content         = tls_private_key.ssh.private_key_pem
  file_permission = "0600"
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = aws_key_pair.main.key_name
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_gb
    delete_on_termination = true
    encrypted             = true

    tags = { Name = "stocksense-root" }
  }

  # Automatiza o §9.2: Docker, plugin compose e o swapfile de 2 GB,
  # que é a rede de proteção contra OOM durante o lote do motor (§6.1).
  user_data = <<-EOT
    #!/bin/bash
    set -euxo pipefail

    apt-get update
    apt-get install -y docker.io docker-compose-v2 git unzip
    usermod -aG docker ubuntu
    systemctl enable --now docker

    # Swapfile de 2 GB (§6.1) — obrigatório: o orçamento de memória fecha em 3,9 GB de 4 GB
    if [ ! -f /swapfile ]; then
      fallocate -l 2G /swapfile
      chmod 600 /swapfile
      mkswap /swapfile
      swapon /swapfile
      echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi

    # AWS CLI, usado pelo cron de backup do §9.7
    curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscli.zip
    unzip -q /tmp/awscli.zip -d /tmp
    /tmp/aws/install
    rm -rf /tmp/awscli.zip /tmp/aws

    touch /var/log/stocksense-bootstrap-done
  EOT

  # Recria a instância se o user_data mudar
  user_data_replace_on_change = true

  tags = { Name = "stocksense-app" }
}

# IPv4 público é cobrado desde 2024 (~US$ 3,6/mês), inclusive com a instância
# PARADA (§4.2). É o custo que continua correndo quando você desliga para economizar.
resource "aws_eip" "app" {
  instance = aws_instance.app.id
  domain   = "vpc"

  tags = { Name = "stocksense-eip" }

  depends_on = [aws_internet_gateway.main]
}
