#
# artifact-registry/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospedará o OCI Artifact Registry."
  type        = string
}

variable "region_key" {
  description = "Chave da região do repositório: gru ou vcp."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}
