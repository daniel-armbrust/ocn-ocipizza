#
# drg/route-distribution.tf
#

# Importa rotas anunciadas pelas VCNs spoke e pelo Remote Peering.
resource "oci_core_drg_route_distribution" "from_firewall" {
  drg_id            = oci_core_drg.this.id
  display_name      = "from-firewall-import"
  distribution_type = "IMPORT"
}

# Importa as rotas anunciadas pela VCN-FIREWALL para o Remote Peering.
resource "oci_core_drg_route_distribution" "remote_peering" {
  drg_id            = oci_core_drg.this.id
  display_name      = "remote-peering-import"
  distribution_type = "IMPORT"
}
