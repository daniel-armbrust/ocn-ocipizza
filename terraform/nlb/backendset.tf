#
# nlb/backendset.tf
#

# Cada porta publicada possui um backend set com preservação da origem.
resource "oci_network_load_balancer_backend_set" "this" {
  for_each                 = local.backend_sets
  name                     = each.value.name
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.this.id
  policy                   = "FIVE_TUPLE"
  is_preserve_source       = true

  health_checker {
    protocol = "TCP"
    # O backend aceita qualquer porta; a verificação usa o SSH como porta
    # estável de teste da disponibilidade do firewall.
    port               = var.health_check_port
    interval_in_millis = 10000
    timeout_in_millis  = 3000
    retries            = 3
  }
}
