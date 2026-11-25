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

  # Desabilita a exportação dinâmica para impedir que rotas aprendidas pelo
  # RPC sejam refletidas durante o teste de roteamento cross-region.
  remove_export_drg_route_distribution_trigger = true
}

resource "oci_core_drg_attachment_management" "vcp_remote_peering" {
  provider = oci.vcp

  attachment_type    = "REMOTE_PEERING_CONNECTION"
  compartment_id     = var.compartment_id
  drg_id             = module.drg_vcp.drg_id
  network_id         = oci_core_remote_peering_connection.vcp.id
  drg_route_table_id = module.drg_vcp.route_table_ids.remote_peering

  # Mantém em VCP o mesmo comportamento adotado em GRU.
  remove_export_drg_route_distribution_trigger = true
}

# Depois da inspeção em GRU, encaminha as redes de VCP ao RPC local.
resource "oci_core_drg_route_table_route_rule" "gru_from_firewall_to_vcp" {
  provider = oci.gru

  for_each = toset([
    "10.80.0.0/16", # VCN-FIREWALL-VCP
    "10.81.0.0/16", # VCN-OKE-VCP
    "10.82.0.0/16", # VCN-DB-VCP
    "10.84.0.0/16", # VCN-SERVICES-VCP
  ])

  drg_route_table_id         = module.drg_gru.route_table_ids.from_firewall
  destination                = each.value
  destination_type           = "CIDR_BLOCK"
  next_hop_drg_attachment_id = oci_core_drg_attachment_management.gru_remote_peering.id
}

# Depois da inspeção em VCP, encaminha as redes de GRU ao RPC local.
resource "oci_core_drg_route_table_route_rule" "vcp_from_firewall_to_gru" {
  provider = oci.vcp

  for_each = toset([
    "10.70.0.0/16", # VCN-FIREWALL-GRU
    "10.71.0.0/16", # VCN-OKE-GRU
    "10.72.0.0/16", # VCN-DB-GRU
    "10.74.0.0/16", # VCN-SERVICES-GRU
  ])

  drg_route_table_id         = module.drg_vcp.route_table_ids.from_firewall
  destination                = each.value
  destination_type           = "CIDR_BLOCK"
  next_hop_drg_attachment_id = oci_core_drg_attachment_management.vcp_remote_peering.id
}
