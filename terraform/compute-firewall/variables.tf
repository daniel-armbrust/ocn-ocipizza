#
# compute-firewall/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment da instância de firewall."
  type        = string
}

variable "region_key" {
  description = "Chave da região da instância: gru ou vcp."
  type        = string
}

variable "firewall_index" {
  description = "Índice da instância de firewall dentro da região."
  type        = number
  default     = 1

  validation {
    condition     = var.firewall_index >= 1
    error_message = "O índice do firewall deve ser maior ou igual a 1."
  }
}

variable "subnet_ids" {
  description = "Sub-rede privada que hospeda as VNICs do firewall."
  type = object({
    firewall = string
  })
}

variable "ssh_public_key" {
  description = "Chave pública SSH opcional para acesso administrativo."
  type        = string
  default     = null
}
