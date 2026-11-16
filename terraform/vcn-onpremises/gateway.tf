#
# vcn-onpremises/gateway.tf
#

# O Internet Gateway representa a saída pública do ambiente on-premises
# simulado. A futura conexão VPN será adicionada separadamente.
resource "oci_core_internet_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "igw"
  enabled        = true
}
