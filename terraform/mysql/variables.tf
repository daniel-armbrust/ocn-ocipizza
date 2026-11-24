#
# mysql/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment dos recursos MySQL HeatWave."
  type        = string
}

variable "region_key" {
  description = "Chave curta da região usada nos nomes dos recursos."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}

variable "subnet_id" {
  description = "OCID da sub-rede privada destinada ao MySQL."
  type        = string
}

variable "admin_username" {
  description = "Nome do usuário administrador do MySQL."
  type        = string
  default     = "ocipizza_admin"
}

variable "admin_password" {
  description = "Senha do administrador do MySQL."
  type        = string
  sensitive   = true

  validation {
    condition = (
      length(var.admin_password) >= 8 &&
      length(var.admin_password) <= 32 &&
      can(regex("[0-9]", var.admin_password)) &&
      can(regex("[a-z]", var.admin_password)) &&
      can(regex("[A-Z]", var.admin_password)) &&
      can(regex("[^[:alnum:]]", var.admin_password))
    )
    error_message = "admin_password deve ter entre 8 e 32 caracteres e conter número, letra minúscula, letra maiúscula e caractere especial."
  }
}
