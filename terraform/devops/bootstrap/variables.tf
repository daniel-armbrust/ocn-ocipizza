#
# devops/bootstrap/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que contém os recursos usados pelos bootstraps."
  type        = string
}

variable "project_id" {
  description = "OCID do projeto OCI DevOps que hospedará as pipelines de bootstrap."
  type        = string
}

variable "repository_id" {
  description = "OCID do Code Repository espelhado que contém os scripts de bootstrap."
  type        = string
}

variable "repository_url" {
  description = "URL HTTP do Code Repository espelhado que contém os scripts de bootstrap."
  type        = string

  validation {
    condition     = length(trimspace(var.repository_url)) > 0
    error_message = "repository_url não pode ser vazia."
  }
}

variable "repository_branch" {
  description = "Branch do Code Repository consumida pelos Managed Build stages."
  type        = string
  default     = "main"

  validation {
    condition     = length(trimspace(var.repository_branch)) > 0
    error_message = "repository_branch não pode ser vazia."
  }
}

variable "private_subnet_id" {
  description = "OCID da subnet privada usada pelos Managed Build stages de bootstrap."
  type        = string
}
