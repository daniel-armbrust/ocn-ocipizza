#
# gru_drg.tf
#   - DRG e Attachments da região GRU.
#

resource "oci_core_drg" "gru_drg-appl" {
    provider = oci.gru
    
    compartment_id = var.compartment_id
    display_name = "drg-appl"    
}

resource "oci_core_drg" "gru_drg-db" {
    provider = oci.gru
    
    compartment_id = var.compartment_id
    display_name = "drg-db"    
}

#--------------#
# vcn-firewall #
#--------------#

# drg-appl
resource "oci_core_drg_attachment" "gru_drg-appl_vcn-firewall_attch" {
    provider = oci.gru

    drg_id = oci_core_drg.gru_drg-appl.id
    display_name = "drg-appl_vcn-firewall_attch"

    network_details {
        id = oci_core_vcn.gru_vcn-firewall.id
        type = "VCN" 

        // Utiliza a tabela "vcn-firewall_route-table" (FIREWALL PRIVATE IP)
        route_table_id =  oci_core_route_table.gru_drg-appl_vcn-firewall_attch_route-table.id
    }

    // Utiliza a tabela "FROM-FIREWALL"
    drg_route_table_id = oci_core_drg_route_table.gru_drg-appl_from-firewall_route-table.id
}

#------------#
# vcn-appl-1 #
#------------#

# drg-appl
resource "oci_core_drg_attachment" "gru_drg-appl_vcn-appl-1_attch" {
    provider = oci.gru

    drg_id = oci_core_drg.gru_drg-appl.id
    display_name = "drg-appl_vcn-appl-1_attch"

    network_details {
        id = oci_core_vcn.gru_vcn-appl-1.id
        type = "VCN"      
    }

    // Utiliza a tabela "TO-FIREWALL"
    drg_route_table_id = oci_core_drg_route_table.gru_drg-appl_to-firewall_route-table.id
}

#------------#
# vcn-appl-2 #
#------------#

# drg-appl
resource "oci_core_drg_attachment" "gru_drg-appl_vcn-appl-2_attch" {
    provider = oci.gru

    drg_id = oci_core_drg.gru_drg-appl.id
    display_name = "drg-appl_vcn-appl-2_attch"

    network_details {
        id = oci_core_vcn.gru_vcn-appl-2.id
        type = "VCN"      
    }

    // Utiliza a tabela "TO-FIREWALL"
    drg_route_table_id = oci_core_drg_route_table.gru_drg-appl_to-firewall_route-table.id
}

#--------------#
# vcn-internet #
#--------------#

# drg-appl
resource "oci_core_drg_attachment" "gru_drg-appl_vcn-internet_attch" {
    provider = oci.gru

    drg_id = oci_core_drg.gru_drg-appl.id
    display_name = "drg-appl_vcn-internet_attch"

    network_details {
        id = oci_core_vcn.gru_vcn-internet.id
        type = "VCN"      
    }

    // Utiliza a tabela "TO-FIREWALL"
    drg_route_table_id = oci_core_drg_route_table.gru_drg-appl_to-firewall_route-table.id
}

#--------#
# vcn-db #
#--------#

# drg-db
resource "oci_core_drg_attachment" "gru_drg-db_vcn-db_attch" {
    provider = oci.gru

    drg_id = oci_core_drg.gru_drg-db.id
    display_name = "drg-db_vcn-db_attch"

    network_details {
        id = oci_core_vcn.gru_vcn-db.id
        type = "VCN"      
    }   

    // Utiliza a tabela "vcn-db_attch_route-table"
    drg_route_table_id = oci_core_drg_route_table.gru_drg-db_vcn-db_attch_route-table.id
}