#
# nlb/nlb.tf
#

# NLB privado de camada 4. O modo preserve source/destination mantém os
# endereços originais e evita que o NLB funcione como proxy de aplicação.
resource "oci_network_load_balancer_network_load_balancer" "this" {
  compartment_id                 = var.compartment_id
  display_name                   = "nlb-firewall-${var.region_key}"
  subnet_id                      = var.subnet_id
  is_private                     = true
  is_preserve_source_destination = true
  is_symmetric_hash_enabled      = true
}
