#
# public-ip/reserved-ip.tf
#

# Reserva um IP público regional para ser associado posteriormente ao LB.
resource "oci_core_public_ip" "load_balancer" {
  compartment_id = var.compartment_id
  display_name   = local.display_name
  lifetime       = "RESERVED"
}
