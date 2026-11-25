#
# drg/route-table.tf
#

# A tabela to-firewall-drg-rt recebe o tráfego dos spokes e o encaminha ao
# firewall.
resource "oci_core_drg_route_table" "to_firewall" {
  drg_id       = oci_core_drg.this.id
  display_name = "to-firewall-drg-rt"
}

# A tabela from-firewall-drg-rt importa as rotas dos spokes locais. As redes
# remotas são configuradas estaticamente no módulo raiz após a criação do RPC.
resource "oci_core_drg_route_table" "from_firewall" {
  drg_id                           = oci_core_drg.this.id
  display_name                     = "from-firewall-drg-rt"
  import_drg_route_distribution_id = oci_core_drg_route_distribution.from_firewall.id
}

# A tabela remote-peering-drg-rt é exclusiva dos attachments RPC regionais.
# Sua distribuição de importação permanece vazia e a tabela utiliza somente
# rotas estáticas para os spokes locais via VCN-FIREWALL.
resource "oci_core_drg_route_table" "remote_peering" {
  drg_id                           = oci_core_drg.this.id
  display_name                     = "remote-peering-drg-rt"
  import_drg_route_distribution_id = oci_core_drg_route_distribution.remote_peering.id
}
