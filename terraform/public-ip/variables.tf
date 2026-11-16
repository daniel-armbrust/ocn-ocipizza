#
# public-ip/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que receberá o endereço IP reservado."
  type        = string
}

variable "region_key" {
  description = "Chave curta da região usada no nome administrativo do IP."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}
