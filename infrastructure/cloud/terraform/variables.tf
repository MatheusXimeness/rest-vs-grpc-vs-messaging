variable "regiao" {
  description = "Região da AWS. us-east-1 é a mais barata; sa-east-1 (São Paulo) custa ~50% a mais."
  type        = string
  default     = "us-east-1"
}

variable "tipo_instancia" {
  description = <<-EOT
    Tipo da VM. Os contêineres somam 9 CPUs de limite (4 serviços × 1,0 + 4 bancos × 0,5 +
    broker 1,0 + k6 2,0) e ~4,5 GB de memória, então a VM precisa de folga acima disso,
    como a máquina local (12 CPUs lógicas). c6i.4xlarge: 16 vCPUs, 32 GB, ~US$ 0,68/h.
  EOT
  type        = string
  default     = "c6i.4xlarge"
}

variable "chave_publica_ssh" {
  description = "Caminho da chave pública SSH usada para acessar a VM."
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "meu_ip" {
  description = "IP (CIDR /32) autorizado a acessar a VM por SSH. O nuvem.sh preenche automaticamente."
  type        = string
}

variable "disco_gb" {
  description = "Tamanho do disco (GB). Imagens Docker + resultados cabem em 30 GB."
  type        = number
  default     = 30
}
