#
# vcn-onpremises/vcn.tf
#

resource "oci_core_vcn" "this" {
  compartment_id                   = var.compartment_id
  cidr_blocks                      = [local.vcn.cidr_block]
  ipv6private_cidr_blocks          = [local.vcn.ipv6_cidr_block]
  is_ipv6enabled                   = true
  is_oracle_gua_allocation_enabled = false
  display_name                     = local.vcn.name
  dns_label                        = local.vcn.dns_label
}
