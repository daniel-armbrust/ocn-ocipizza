#
# email-delivery/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda os recursos do Email Delivery."
  type        = string
}

variable "region_key" {
  description = "Identificador curto da região, utilizado no seletor DKIM."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}
