#
# public-ip/reserved-ip.tf
#

# Mantém um endereço IPv4 estável para o Load Balancer público da aplicação.
resource "oci_core_public_ip" "load_balancer" {
  compartment_id = var.compartment_id
  display_name   = local.display_name
  lifetime       = "RESERVED"
}
