#
# logging/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda os logs da aplicação."
  type        = string
}

variable "region_key" {
  description = "Chave curta da região usada para documentar o módulo."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}

variable "devops_project_id" {
  description = "OCID do projeto OCI DevOps cujos Service Logs serão habilitados nesta região."
  type        = string
  default     = null
  nullable    = true
}

variable "enable_devops_log" {
  description = "Define se o Service Log do projeto OCI DevOps será criado nesta região."
  type        = bool
  default     = false
}
