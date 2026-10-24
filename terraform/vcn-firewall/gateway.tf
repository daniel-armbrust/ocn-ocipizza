#
# vcn-firewall/gateway.tf
#

# O NAT Gateway fornece saída para a Internet sem expor as sub-redes privadas.
resource "oci_core_nat_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "ngw"
}

# O SGW permite acesso privado aos serviços suportados da OCI.
resource "oci_core_service_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "sgw"

  services {
    service_id = data.oci_core_services.all.services[0].id
  }
}
