#
# vcn-firewall/variables.tf
#

variable "compartment_id" {
  type = string
}

variable "region_key" {
  description = "Chave da configuração regional da VCN-FIREWALL."
  type        = string
}

variable "drg_id" {
  type    = string
  default = null
}
