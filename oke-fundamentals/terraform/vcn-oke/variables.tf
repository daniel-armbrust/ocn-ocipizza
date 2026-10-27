#
# vcn-oke/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment dos recursos da VCN-OKE."
  type        = string
}

variable "public_access_cidr" {
  description = "CIDR IPv4 público autorizado a acessar o Kubernetes API Server."
  type        = string

  validation {
    condition     = can(cidrhost(var.public_access_cidr, 0)) && can(regex("^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+/32$", var.public_access_cidr))
    error_message = "public_access_cidr deve ser um endereço IPv4 público individual no formato x.x.x.x/32."
  }
}
