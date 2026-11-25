#
# drg/route-distribution-statement.tf
#

# Importa somente as rotas anunciadas pela VCN-OKE.
resource "oci_core_drg_route_distribution_statement" "oke" {
  drg_route_distribution_id = oci_core_drg_route_distribution.from_firewall.id
  action                    = "ACCEPT"
  priority                  = 10

  match_criteria {
    match_type        = "DRG_ATTACHMENT_ID"
    drg_attachment_id = oci_core_drg_attachment.this["oke"].id
  }
}

# Importa somente as rotas anunciadas pela VCN-DB.
resource "oci_core_drg_route_distribution_statement" "db" {
  drg_route_distribution_id = oci_core_drg_route_distribution.from_firewall.id
  action                    = "ACCEPT"
  priority                  = 20

  match_criteria {
    match_type        = "DRG_ATTACHMENT_ID"
    drg_attachment_id = oci_core_drg_attachment.this["db"].id
  }
}

# Importa somente as rotas anunciadas pela VCN-SERVICES.
resource "oci_core_drg_route_distribution_statement" "services" {
  drg_route_distribution_id = oci_core_drg_route_distribution.from_firewall.id
  action                    = "ACCEPT"
  priority                  = 25

  match_criteria {
    match_type        = "DRG_ATTACHMENT_ID"
    drg_attachment_id = oci_core_drg_attachment.this["services"].id
  }
}
