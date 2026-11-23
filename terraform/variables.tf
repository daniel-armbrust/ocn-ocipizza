#
# variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que receberá os recursos do OCI Pizza."
  type        = string
}

variable "tenancy_id" {
  description = "OCID da tenancy usado para criar dynamic groups e policies no root compartment."
  type        = string
}

variable "iam_dynamic_group_name" {
  description = "Nome do dynamic group dos workloads do OCI Pizza."
  type        = string
  default     = "ocipizza-instances"
}

variable "iam_policy_name" {
  description = "Nome da policy dos Instance Principals do OCI Pizza."
  type        = string
  default     = "ocipizza-instance-principals"
}

variable "devops_dynamic_group_name" {
  description = "Nome do dynamic group dos resource principals do OCI DevOps."
  type        = string
  default     = "ocipizza-devops"
}

variable "devops_policy_name" {
  description = "Nome da policy utilizada pelas pipelines do OCI DevOps."
  type        = string
  default     = "ocipizza-devops"
}

variable "service_principals_policy_name" {
  description = "Nome da policy dos serviços gerenciados utilizados pelo OCI Pizza."
  type        = string
  default     = "ocipizza-service-principals"
}

variable "firewall_ssh_public_key" {
  description = "Conteúdo da chave pública SSH instalada nos Compute Firewalls."
  type        = string
}

variable "oke_worker_ssh_public_key" {
  description = "Conteúdo da chave pública SSH instalada nos worker nodes do OKE."
  type        = string
}

variable "notification_email" {
  description = "Endereço de e-mail inscrito no Topic usado pelo OCI DevOps."
  type        = string

  validation {
    condition     = can(regex("^[^@[:space:]]+@[^@[:space:]]+\\.[^@[:space:]]+$", var.notification_email))
    error_message = "notification_email deve conter um endereço de e-mail válido."
  }
}

variable "github_pat" {
  description = "Personal Access Token usado pela conexão do OCI DevOps com o GitHub."
  type        = string
  sensitive   = true

  validation {
    condition     = length(trimspace(var.github_pat)) > 0
    error_message = "github_pat não pode ser vazio."
  }
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
