#
# gru_remotepeering.tf
#   - Remote Peering Gateways da região GRU.
#

# drg-appl
resource "oci_core_remote_peering_connection" "gru_drg-appl_remote-peering" {
    provider = oci.gru

    compartment_id = var.compartment_id
    drg_id = oci_core_drg.gru_drg-appl.id
    display_name = "drg-appl_remote-peering"

    peer_id = oci_core_remote_peering_connection.vcp_drg-appl_remote-peering.id
    peer_region_name = "sa-vinhedo-1"
}

# drg-db
resource "oci_core_remote_peering_connection" "gru_drg-db_remote-peering" {
    provider = oci.gru

    compartment_id = var.compartment_id
    drg_id = oci_core_drg.gru_drg-db.id
    display_name = "drg-db_remote-peering"
    
    peer_id = oci_core_remote_peering_connection.vcp_drg-db_remote-peering.id
    peer_region_name = "sa-vinhedo-1"
}