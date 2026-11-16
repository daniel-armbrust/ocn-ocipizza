#
# vcn-firewall/subnet.tf
#

# Cria e associa cada sub-rede ao DHCP, Route Table e Security List corretos.
resource "oci_core_subnet" "this" {
  for_each = local.config.subnets

  compartment_id             = var.compartment_id
  vcn_id                     = oci_core_vcn.this.id
  dhcp_options_id            = oci_core_dhcp_options.this.id
  route_table_id             = local.route_table_ids[each.key]
  security_list_ids          = [local.security_list_ids[each.key]]
  display_name               = each.value.name
  cidr_block                 = each.value.cidr_block
  ipv6cidr_block             = each.value.ipv6_cidr_block
  dns_label                  = each.value.dns_label
  prohibit_public_ip_on_vnic = each.value.prohibit_public_ip
}
