#
# drg/vcn-route-table.tf
#

# Tabela de rotas da VCN-FIREWALL usada pelo tráfego encaminhado pelo DRG.
# Todo destino segue para o NLB do firewall da região atual.
resource "oci_core_route_table" "to_firewall_ip" {
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_ids.firewall
  display_name   = "rt-to-firewall-ip"

  # A única regra atende redes privadas e destinos externos. O NLB encaminha o
  # tráfego ao firewall regional, que seleciona o DRG ou o NAT Gateway.
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = var.nlb_private_ip_id
  }
}
