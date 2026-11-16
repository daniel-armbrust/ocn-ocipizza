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
