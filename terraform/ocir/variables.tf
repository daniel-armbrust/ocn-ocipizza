#
# ocir/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospedará os repositórios do OCI Container Registry."
  type        = string
}

variable "region_key" {
  description = "Chave curta da região OCI usada para compor o endpoint do OCIR."
  type        = string

  validation {
    condition     = length(trimspace(var.region_key)) > 0
    error_message = "region_key não pode ser vazia."
  }
}
