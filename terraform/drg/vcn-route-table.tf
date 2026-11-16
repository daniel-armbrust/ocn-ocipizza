#
# drg/vcn-route-table.tf
#

# Tabela de rotas da VCN-FIREWALL usada pelo tráfego encaminhado pelo DRG.
# Todo o tráfego segue para o IP privado do NLB regional.
resource "oci_core_route_table" "to_firewall_ip" {
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_ids.firewall
  display_name   = "rt-to-firewall-ip"

  route_rules {
    # O NLB distribui o tráfego entre os firewalls sem alterar a origem.
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = var.nlb_private_ip_id
  }
}
