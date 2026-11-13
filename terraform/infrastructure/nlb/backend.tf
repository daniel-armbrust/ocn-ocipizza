#
# nlb/backend.tf
#

# Registra os dois firewalls como backends do NLB.
resource "oci_network_load_balancer_backend" "firewall" {
  for_each                 = local.backends
  backend_set_name         = oci_network_load_balancer_backend_set.this[each.value.backend_set_key].name
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.this.id
  name                     = "backend-${each.key}"
  ip_address               = each.value.ip_address
  # A porta 0 mantém a porta original da conexão encaminhada pelo listener.
  port       = 0
  is_backup  = false
  is_drain   = false
  is_offline = false
}
