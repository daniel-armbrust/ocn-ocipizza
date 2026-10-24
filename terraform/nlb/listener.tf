#
# nlb/listener.tf
#

# O listener ANY na porta 0 encaminha qualquer protocolo e qualquer porta,
# sem terminação TLS ou alteração de payload. A origem é preservada pelo NLB.
resource "oci_network_load_balancer_listener" "this" {
  for_each                 = local.backend_sets
  default_backend_set_name = oci_network_load_balancer_backend_set.this[each.key].name
  name                     = "listener-${each.value.port}"
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.this.id
  port                     = each.value.port
  protocol                 = "ANY"
}
