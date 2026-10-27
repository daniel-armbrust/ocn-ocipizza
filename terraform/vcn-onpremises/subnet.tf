#
# vcn-onpremises/subnet.tf
#

resource "oci_core_subnet" "this" {
  compartment_id             = var.compartment_id
  vcn_id                     = oci_core_vcn.this.id
  dhcp_options_id            = oci_core_dhcp_options.this.id
  route_table_id             = oci_core_route_table.this.id
  security_list_ids          = [oci_core_security_list.this.id]
  display_name               = local.subnet.name
  cidr_block                 = local.subnet.cidr_block
  ipv6cidr_block             = local.subnet.ipv6_cidr_block
  dns_label                  = local.subnet.dns_label
  prohibit_public_ip_on_vnic = local.subnet.prohibit_public_ip
}
