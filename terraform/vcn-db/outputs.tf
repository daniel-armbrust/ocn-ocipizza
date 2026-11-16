#
# vcn-db/outputs.tf
#

output "vcn_id" {
  description = "OCID da VCN-DB regional."
  value       = oci_core_vcn.this.id
}

output "subnet_ids" {
  description = "Mapa das sub-redes da VCN-DB por finalidade."
  value       = { for key, subnet in oci_core_subnet.this : key => subnet.id }
}
