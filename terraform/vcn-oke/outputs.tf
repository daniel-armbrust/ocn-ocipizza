#
# vcn-oke/outputs.tf
#

output "vcn_id" {
  value = oci_core_vcn.this.id
}

output "subnet_ids" {
  value = { for key, subnet in oci_core_subnet.this : key => subnet.id }
}
