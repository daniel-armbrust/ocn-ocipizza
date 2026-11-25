#
# drg/route-distribution.tf
#

# Importa somente as rotas anunciadas pelas VCNs spoke locais.
resource "oci_core_drg_route_distribution" "from_firewall" {
  drg_id            = oci_core_drg.this.id
  display_name      = "from-firewall-import"
  distribution_type = "IMPORT"
}

# Mantida deliberadamente sem statements: a tabela do RPC deve usar somente
# suas rotas estáticas e não importar anúncios de outros attachments do DRG.
resource "oci_core_drg_route_distribution" "remote_peering" {
  drg_id            = oci_core_drg.this.id
  display_name      = "remote-peering-import"
  distribution_type = "IMPORT"
}
