#
# devops/notification-service/variables.tf
#

variable "project_id" {
  description = "OCID do projeto OCI DevOps que hospedará a build pipeline do notification-service."
  type        = string
}

variable "repository_id" {
  description = "OCID do Code Repository espelhado que contém o código do notification-service."
  type        = string
}

variable "repository_url" {
  description = "URL HTTP do Code Repository espelhado que contém o código do notification-service."
  type        = string

  validation {
    condition     = length(trimspace(var.repository_url)) > 0
    error_message = "repository_url não pode ser vazia."
  }
}

variable "repository_branch" {
  description = "Branch do Code Repository consumida pela build pipeline do notification-service."
  type        = string
  default     = "main"

  validation {
    condition     = length(trimspace(var.repository_branch)) > 0
    error_message = "repository_branch não pode ser vazia."
  }
}

variable "private_subnet_id" {
  description = "OCID da subnet privada usada pelo Managed Build runner do notification-service."
  type        = string
}

variable "build_runner_image" {
  description = "Imagem do sistema operacional usada pelo Managed Build runner."
  type        = string
  default     = "OL8_X86_64_STANDARD_10"

  validation {
    condition = contains([
      "OL7_X86_64_STANDARD_10",
      "OL8_X86_64_STANDARD_10",
    ], var.build_runner_image)
    error_message = "build_runner_image deve ser OL7_X86_64_STANDARD_10 ou OL8_X86_64_STANDARD_10."
  }
}

variable "build_runner_ocpus" {
  description = "Quantidade de OCPUs alocada ao Managed Build runner."
  type        = number
  default     = 2

  validation {
    condition     = var.build_runner_ocpus > 0 && floor(var.build_runner_ocpus) == var.build_runner_ocpus
    error_message = "build_runner_ocpus deve ser um número inteiro maior que zero."
  }
}

variable "build_runner_memory_in_gbs" {
  description = "Memória, em GB, alocada ao Managed Build runner."
  type        = number
  default     = 4

  validation {
    condition     = var.build_runner_memory_in_gbs > 0
    error_message = "build_runner_memory_in_gbs deve ser maior que zero."
  }
}
