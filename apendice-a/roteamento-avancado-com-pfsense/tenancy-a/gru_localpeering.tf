#
# gru_localpeering.tf
#   - Local Peering Gateways da região GRU.
#

#---------------------#
# vcn-appl-1 e vcn-db #
#---------------------#

# vcn-appl-1
resource "oci_core_local_peering_gateway" "gru_vcn-appl-1_local-peering" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-appl-1.id
    display_name = "vcn-appl-1_lpg_vcn-db"
    peer_id = oci_core_local_peering_gateway.gru_vcn-db_local-peering.id    
}

# vcn-db
resource "oci_core_local_peering_gateway" "gru_vcn-db_local-peering" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-db.id
    display_name = "vcn-db_lpg_vcn-appl-1"
    #peer_id = oci_core_local_peering_gateway.gru_vcn-appl-1_local-peering.id    
}