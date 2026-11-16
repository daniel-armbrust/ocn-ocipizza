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
