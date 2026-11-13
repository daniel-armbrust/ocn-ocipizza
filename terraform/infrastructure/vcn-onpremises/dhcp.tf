#
# vcn-onpremises/dhcp.tf
#

resource "oci_core_dhcp_options" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = local.vcn.dhcp_options_name

  options {
    type        = "DomainNameServer"
    server_type = "VcnLocalPlusInternet"
  }
}
