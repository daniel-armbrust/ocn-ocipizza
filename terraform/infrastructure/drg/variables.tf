#
# drg/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que receberá o DRG regional."
  type        = string
}

variable "region_key" {
  description = "Chave da região do DRG: gru ou vcp."
  type        = string
}

variable "firewall_trust_private_ip_id" {
  description = "OCID do IP privado da VNIC TRUST do firewall regional."
  type        = string
}

variable "nlb_private_ip_id" {
  description = "OCID do IP privado do NLB regional usado como próximo salto."
  type        = string
}

variable "vcn_ids" {
  description = "IDs das VCNs que serão anexadas ao DRG regional."
  type = object({
    firewall = string
    oke      = string
    db       = string
    ci       = string
    services = string
  })
}
