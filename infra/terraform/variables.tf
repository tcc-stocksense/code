variable "region" {
  description = "Região AWS. us-east-1 é a mais barata (§4.1 do infraestrutura-nuvem.md)."
  type        = string
  default     = "us-east-1"
}

variable "dev_ip" {
  description = <<-EOT
    Seu IP público, em notação CIDR /32 — o único autorizado a abrir SSH.
    Descubra com: curl -s https://checkip.amazonaws.com
    Exemplo: "189.45.12.7/32"
  EOT
  type        = string

  validation {
    condition     = can(cidrnetmask(var.dev_ip))
    error_message = "dev_ip precisa ser um CIDR válido, terminado em /32. Ex.: 189.45.12.7/32"
  }
}

variable "instance_type" {
  description = "t3.medium = 2 vCPU / 4 GB, dimensionada no §6.1."
  type        = string
  default     = "t3.medium"
}

variable "root_volume_gb" {
  description = "EBS gp3: SO + imagens Docker + dados do MySQL (§4.1)."
  type        = number
  default     = 30
}

variable "vpc_cidr" {
  description = "CIDR da VPC dedicada, igual ao diagrama do §3.2."
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "Subnet pública. Pública de propósito: subnet privada exigiria NAT Gateway (§4.2)."
  type        = string
  default     = "10.0.1.0/24"
}

variable "backup_retention_days" {
  description = "Dias até o lifecycle do S3 apagar um dump antigo."
  type        = number
  default     = 30
}
