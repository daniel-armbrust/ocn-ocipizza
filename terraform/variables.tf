#
# variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que receberá a VCN-FIREWALL."
  type        = string
}

variable "oci_config_profile" {
  description = "Profile usado no arquivo de configuração do OCI."
  type        = string
  default     = "DEFAULT"
}
