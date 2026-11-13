#
# valkey/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda o cluster OCI Cache."
  type        = string
}

variable "region_key" {
  description = "Chave curta da região usada no nome do cluster."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}

variable "subnet_id" {
  description = "OCID da sub-rede privada onde o cluster será criado."
  type        = string
}
