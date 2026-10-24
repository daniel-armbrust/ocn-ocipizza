#
# remote-peering.tf
#

# RPC criado em São Paulo. Este lado inicia o pareamento com Vinhedo.
resource "oci_core_remote_peering_connection" "gru" {
  provider = oci.gru

  compartment_id = var.compartment_id
  drg_id         = module.drg_gru.drg_id
  display_name   = "rpc-gru-vcp"

  peer_id          = oci_core_remote_peering_connection.vcp.id
  peer_region_name = local.regions.vcp
}

# RPC criado em Vinhedo. O pareamento é solicitado pelo RPC de GRU.
resource "oci_core_remote_peering_connection" "vcp" {
  provider = oci.vcp

  compartment_id = var.compartment_id
  drg_id         = module.drg_vcp.drg_id
  display_name   = "rpc-vcp-gru"
}

# O attachment de RPC é criado automaticamente pelo OCI quando o RPC existe.
# Este recurso apenas associa o attachment à tabela de rotas do DRG.
resource "oci_core_drg_attachment_management" "gru_remote_peering" {
  provider = oci.gru

  attachment_type    = "REMOTE_PEERING_CONNECTION"
  compartment_id     = var.compartment_id
  drg_id             = module.drg_gru.drg_id
  network_id         = oci_core_remote_peering_connection.gru.id
  drg_route_table_id = module.drg_gru.route_table_ids.remote_peering
}

resource "oci_core_drg_attachment_management" "vcp_remote_peering" {
  provider = oci.vcp

  attachment_type    = "REMOTE_PEERING_CONNECTION"
  compartment_id     = var.compartment_id
  drg_id             = module.drg_vcp.drg_id
  network_id         = oci_core_remote_peering_connection.vcp.id
  drg_route_table_id = module.drg_vcp.route_table_ids.remote_peering
}
