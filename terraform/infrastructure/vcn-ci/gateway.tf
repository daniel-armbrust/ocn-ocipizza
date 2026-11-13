#
# vcn-ci/gateway.tf
#

# Container Instances acessa serviços OCI sem exposição direta à Internet.
resource "oci_core_service_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "sgw"

  services {
    service_id = data.oci_core_services.all.services[0].id
  }
}

# O Internet Gateway expõe somente a sub-rede pública de load balancers.
resource "oci_core_internet_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "igw"
  enabled        = true
}
