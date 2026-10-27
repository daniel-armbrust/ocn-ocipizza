#
# vcn-onpremises/outputs.tf
#

output "vcn_id" {
  description = "OCID da VCN on-premises simulada em GRU."
  value       = oci_core_vcn.this.id
}

output "subnet_id" {
  description = "OCID da sub-rede pública on-premises simulada."
  value       = oci_core_subnet.this.id
}
