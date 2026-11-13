#
# variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que receberá a VCN-FIREWALL."
  type        = string
}

variable "firewall_ssh_public_key" {
  description = "Chave pública SSH opcional instalada nos Compute Firewalls."
  type        = string
  default     = null
  nullable    = true
}

variable "oke_worker_ssh_public_key" {
  description = "Chave pública SSH opcional instalada nos worker nodes do OKE."
  type        = string
  default     = null
  nullable    = true
}
