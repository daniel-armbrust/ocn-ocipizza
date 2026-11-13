#
# vcn-services/gateway.tf
#

# Permite acesso privado aos serviços hospedados na rede de serviços OCI.
resource "oci_core_service_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "sgw"

  services {
    service_id = data.oci_core_services.all.services[0].id
  }
}
