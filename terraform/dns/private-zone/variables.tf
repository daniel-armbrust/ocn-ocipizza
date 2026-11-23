#
# dns/private-zone/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda os recursos do DNS privado."
  type        = string
}

variable "region_key" {
  description = "Identificador curto da região onde a zona privada será criada."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}

variable "vcn_ids" {
  description = "Mapa das VCNs cujos resolvers devem consultar a zona privada."
  type        = map(string)

  validation {
    condition = (
      length(var.vcn_ids) == 4
      && contains(keys(var.vcn_ids), "firewall")
      && contains(keys(var.vcn_ids), "oke")
      && contains(keys(var.vcn_ids), "db")
      && contains(keys(var.vcn_ids), "services")
    )
    error_message = "vcn_ids deve conter somente as chaves firewall, oke, db e services."
  }
}
