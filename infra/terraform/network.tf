# Rede — camada 1 do §3.2. Nenhum destes recursos é cobrado pela AWS.

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "stocksense-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = { Name = "stocksense-igw" }
}

# Subnet PÚBLICA por decisão de projeto: a EC2 sai para a internet pelo IGW.
# Subnet privada exigiria NAT Gateway (~US$ 32/mês), um terço do crédito (§4.2).
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = { Name = "stocksense-subnet-public" }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = { Name = "stocksense-rt-public" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# SG-web — a camada que de fato isola o sistema (§ "O que de fato isola o banco").
# O Docker fura o firewall do host (ufw), mas não fura o Security Group:
# ele é aplicado na ENI, fora do sistema operacional.
resource "aws_security_group" "web" {
  name        = "stocksense-sg-web"
  description = "Entrada: 443/80 publicos, 22 restrito ao dev. Saida liberada."
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS - unico ponto de entrada da aplicacao (Caddy)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP - redirect para HTTPS e desafio ACME do Lets Encrypt (Parte 5)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH - apenas o IP do desenvolvedor"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.dev_ip]
  }

  egress {
    description = "Saida liberada - apt, Docker Hub, ACME, S3"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "stocksense-sg-web" }
}

# NOTA: não há regra para 8080, 8000 ou 3306. Backend, ml-service e MySQL
# são alcançáveis apenas pela rede interna do Docker (R6 e §9.4).
