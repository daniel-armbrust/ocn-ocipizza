#
# vcn-services/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment dos recursos da VCN-SERVICES."
  type        = string
}

variable "region_key" {
  description = "Chave da configuração regional da VCN-SERVICES."
  type        = string
}

variable "drg_id" {
  description = "OCID do DRG regional usado pela sub-rede privada."
  type        = string
  default     = null
}
