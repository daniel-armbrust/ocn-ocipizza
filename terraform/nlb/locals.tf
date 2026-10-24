#
# nlb/locals.tf
#

locals {
  # Cada porta possui um backend set próprio, pois o backend recebe o mesmo
  # número de porta encaminhado pelo listener.
  backend_sets = {
    for port in var.listener_ports : tostring(port) => {
      name = "backendset-firewall"
      port = port
    }
  }

  # Expande as duas combinações de firewalls para cada backend set.
  backends = {
    for item in flatten([
      for backend_set in local.backend_sets : [
        for firewall_index, firewall_ip in var.firewall_ips : {
          # A chave usa somente valores conhecidos durante o plan. O IP do
          # firewall fica no valor e pode ser resolvido durante o apply.
          key             = "${backend_set.port}-${firewall_index + 1}"
          backend_set_key = tostring(backend_set.port)
          ip_address      = firewall_ip
          port            = backend_set.port
        }
      ]
    ]) : item.key => item
  }
}
