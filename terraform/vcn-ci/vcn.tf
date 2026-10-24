#
# vcn-ci/vcn.tf
#

resource "oci_core_vcn" "this" {
  compartment_id                   = var.compartment_id
  cidr_blocks                      = [local.config.cidr_block]
  ipv6private_cidr_blocks          = [local.config.ipv6_cidr_block]
  is_ipv6enabled                   = true
  is_oracle_gua_allocation_enabled = false
  display_name                     = local.config.name
  dns_label                        = local.config.dns_label
}
