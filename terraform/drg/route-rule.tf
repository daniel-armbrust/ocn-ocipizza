#
# drg/route-rule.tf
#

# Encaminha o tráfego padrão dos spokes para o attachment do firewall.
resource "oci_core_drg_route_table_route_rule" "to_firewall_default" {
  drg_route_table_id         = oci_core_drg_route_table.to_firewall.id
  destination                = "0.0.0.0/0"
  destination_type           = "CIDR_BLOCK"
  next_hop_drg_attachment_id = oci_core_drg_attachment.this["firewall"].id
}

# Quando o tráfego chega pelo RPC, encaminha cada rede spoke local para o
# attachment da VCN-FIREWALL. Essas rotas impedem que o tráfego cross-region
# alcance diretamente os attachments de OKE, banco de dados ou serviços.
resource "oci_core_drg_route_table_route_rule" "remote_peering_to_spokes_via_firewall" {
  for_each = toset(local.config.spoke_cidr_blocks)

  drg_route_table_id         = oci_core_drg_route_table.remote_peering.id
  destination                = each.value
  destination_type           = "CIDR_BLOCK"
  next_hop_drg_attachment_id = oci_core_drg_attachment.this["firewall"].id
}
