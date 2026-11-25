#
# drg/vcn-route-table.tf
#

# Tabela de rotas da VCN-FIREWALL usada pelo tráfego encaminhado pelo DRG.
# As redes locais e remotas seguem para o NLB do firewall da região atual.
resource "oci_core_route_table" "to_firewall_ip" {
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_ids.firewall
  display_name   = "rt-to-firewall-ip"

  # Encaminha destinos externos ao NLB para que a saída à Internet passe pelo
  # firewall regional e, depois da inspeção, pelo NAT Gateway.
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = var.nlb_private_ip_id
  }

  dynamic "route_rules" {
    for_each = toset(local.inspection_cidr_blocks)

    content {
      # O NLB distribui o tráfego entre os firewalls sem alterar a origem.
      destination       = route_rules.value
      destination_type  = "CIDR_BLOCK"
      network_entity_id = var.nlb_private_ip_id
    }
  }
}
