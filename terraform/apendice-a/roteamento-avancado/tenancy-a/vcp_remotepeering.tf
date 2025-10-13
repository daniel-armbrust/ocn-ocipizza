#
# vcp_remotepeering.tf
#   - Remote Peering Gateways da região VCP.
#

# drg-appl
resource "oci_core_remote_peering_connection" "vcp_drg-appl_remote-peering" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    drg_id = oci_core_drg.vcp_drg-appl.id
    display_name = "drg-appl_remote-peering"
}

# drg-db
resource "oci_core_remote_peering_connection" "vcp_drg-db_remote-peering" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    drg_id = oci_core_drg.vcp_drg-db.id
    display_name = "drg-db_remote-peering"
}