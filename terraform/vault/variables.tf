#
# vault/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda o Vault persistente."
  type        = string
}

variable "region" {
  description = "Região onde o Vault persistente será criado."
  type        = string
}

variable "github_pat" {
  description = "Personal Access Token armazenado no Secret do OCI Vault."
  type        = string
  sensitive   = true
}

variable "ocir_username" {
  description = "Username completo usado para autenticação no OCIR."
  type        = string

  validation {
    condition     = length(trimspace(var.ocir_username)) > 0
    error_message = "ocir_username não pode ser vazio."
  }
}

variable "ocir_auth_token" {
  description = "Auth Token armazenado no Secret de credenciais do OCIR."
  type        = string
  sensitive   = true

  validation {
    condition     = length(trimspace(var.ocir_auth_token)) > 0
    error_message = "ocir_auth_token não pode ser vazio."
  }
}
