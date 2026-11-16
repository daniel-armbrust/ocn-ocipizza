#
# drg/attachments.tf
#

# Anexa as VCNs regionais ao DRG.
resource "oci_core_drg_attachment" "this" {
  for_each = local.attachments

  drg_id       = oci_core_drg.this.id
  display_name = each.value.name

  # network_details identifica a VCN anexada ao DRG.
  network_details {
    id             = each.value.vcn_id
    type           = "VCN"
    route_table_id = each.key == "firewall" ? oci_core_route_table.to_firewall_ip.id : null
  }

  # drg_route_table_id associa a tabela de rotas interna do DRG.
  # O atributo route_table_id não deve ser usado aqui, pois representa uma
  # tabela de rotas da VCN e pode causar erro 404 durante a criação.
  drg_route_table_id = each.key == "firewall" ? oci_core_drg_route_table.from_firewall.id : oci_core_drg_route_table.to_firewall.id
}
