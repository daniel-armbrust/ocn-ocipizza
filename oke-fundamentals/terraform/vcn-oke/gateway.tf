#
# vcn-oke/gateway.tf
#

# OKE usa o Service Gateway para acessar serviços OCI sem exposição pública.
resource "oci_core_service_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "sgw"

  services {
    service_id = data.oci_core_services.all.services[0].id
  }
}

# O Internet Gateway é usado pelas sub-redes públicas de load balancers e API.
resource "oci_core_internet_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "igw"
  enabled        = true
}

# Os worker nodes permanecem privados e usam o NAT Gateway para acesso externo.
resource "oci_core_nat_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "ngw"
}
