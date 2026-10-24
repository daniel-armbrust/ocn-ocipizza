#
# vcn-oke/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment dos recursos da VCN-OKE."
  type        = string
}

variable "region_key" {
  description = "Chave da configuração regional da VCN-OKE."
  type        = string
}

variable "drg_id" {
  description = "OCID do DRG regional usado pelas sub-redes privadas."
  type        = string
  default     = null
}
