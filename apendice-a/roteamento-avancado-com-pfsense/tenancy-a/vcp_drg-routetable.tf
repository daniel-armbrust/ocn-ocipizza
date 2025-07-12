#
# vcp_drg-routetable.tf
#   - Tabelas de Roteamento do DRG da região VCP.
#

#--------------------------#
# VCN-FIREWALL ROUTE TABLE #
#--------------------------#

resource "oci_core_route_table" "vcp_drg-appl_vcn-firewall_attch_route-table" {   
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-firewall.id
    display_name = "vcn-firewall_route-table"

    // FIREWALL PRIVATE IP
    route_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"   
        network_entity_id = data.oci_core_private_ips.vcp_vm_firewall_vnic_lan_private-ip.private_ips[0]["id"]
    }   
}

#-------------#
# TO-FIREWALL #
#-------------#

# DRG Import Route Distribution
resource "oci_core_drg_route_distribution" "vcp_drg-appl_to-firewall_route-import" {
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-appl.id
    distribution_type = "IMPORT"
    display_name = "to-firewall_route-import"
}

# DRG Route Table
resource "oci_core_drg_route_table" "vcp_drg-appl_to-firewall_route-table" {  
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-appl.id   
    display_name = "to-firewall_route-table"    
}

# DRG Route Table Rules
resource "oci_core_drg_route_table_route_rule" "vcp_drg-appl_to-firewall_route-table_rules" {
    provider = oci.vcp

    drg_route_table_id = oci_core_drg_route_table.vcp_drg-appl_to-firewall_route-table.id
    
    destination = "0.0.0.0/0"
    destination_type = "CIDR_BLOCK"
    next_hop_drg_attachment_id = oci_core_drg_attachment.vcp_drg-appl_vcn-firewall_attch.id
}

#---------------#
# FROM-FIREWALL #
#---------------#

# DRG Import Route Distribution
resource "oci_core_drg_route_distribution" "vcp_drg-appl_from-firewall_route-import" {
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-appl.id
    distribution_type = "IMPORT"
    display_name = "from-firewall_route-import"
}

# DRG Import Route Distribution Statements
resource "oci_core_drg_route_distribution_statement" "vcp_drg-appl_from-firewall_route-import_statement" {
    provider = oci.vcp

    drg_route_distribution_id = oci_core_drg_route_distribution.vcp_drg-appl_from-firewall_route-import.id
    
    action = "ACCEPT"
    priority = 1

    match_criteria {
        match_type = "MATCH_ALL"
    }    
}

# DRG Route Table
resource "oci_core_drg_route_table" "vcp_drg-appl_from-firewall_route-table" {  
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-appl.id   
    import_drg_route_distribution_id = oci_core_drg_route_distribution.vcp_drg-appl_from-firewall_route-import.id
    display_name = "from-firewall_route-table"    
}

#-------------------------#
# DRG-APPL REMOTE-PEERING #
#-------------------------#

# DRG Import Route Distribution
resource "oci_core_drg_route_distribution" "vcp_drg-appl_remote-peering_route-import" {
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-appl.id
    distribution_type = "IMPORT"
    display_name = "drg-appl_remote-peering_route-import"
}

# DRG Import Route Distribution Statements
resource "oci_core_drg_route_distribution_statement" "vcp_drg-appl_remote-peering_route-import_statement" {
    provider = oci.vcp

    drg_route_distribution_id = oci_core_drg_route_distribution.vcp_drg-appl_remote-peering_route-import.id
    
    action = "ACCEPT"
    priority = 1

    match_criteria {
        match_type = "DRG_ATTACHMENT_TYPE"
        attachment_type = "VCN"                   
    }    
}

# DRG Route Table
resource "oci_core_drg_route_table" "vcp_drg-appl_remote-peering_route-table" {  
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-appl.id 
    import_drg_route_distribution_id = oci_core_drg_route_distribution.vcp_drg-appl_remote-peering_route-import.id   
    display_name = "drg-appl_remote-peering_route-table"    
}

resource "oci_core_drg_attachment_management" "vcp_drg-appl_remote-peering_attch" {
  provider = oci.vcp

  compartment_id = var.compartment_id
  drg_id = oci_core_drg.vcp_drg-appl.id
  display_name = "drg-appl_remote-peering_attch"

  attachment_type = "REMOTE_PEERING_CONNECTION"  
  network_id = oci_core_remote_peering_connection.vcp_drg-appl_remote-peering.id
  drg_route_table_id = oci_core_drg_route_table.vcp_drg-appl_remote-peering_route-table.id
}

#--------------#
# VCN-DB ATTCH #
#--------------#

# DRG Import Route Distribution
resource "oci_core_drg_route_distribution" "vcp_drg-db_vcn-db_attch_route-import" {
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-db.id
    distribution_type = "IMPORT"
    display_name = "vcn-db_attch_route-import"
}

# DRG Import Route Distribution Statements
resource "oci_core_drg_route_distribution_statement" "vcp_drg-db_vcn-db_attch_route-import_statement" {
    provider = oci.vcp

    drg_route_distribution_id = oci_core_drg_route_distribution.vcp_drg-db_vcn-db_attch_route-import.id
    
    action = "ACCEPT"
    priority = 1

    match_criteria {
        match_type = "DRG_ATTACHMENT_TYPE"
        attachment_type = "REMOTE_PEERING_CONNECTION"                   
    }    
}

# DRG Route Table
resource "oci_core_drg_route_table" "vcp_drg-db_vcn-db_attch_route-table" {  
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-db.id 
    import_drg_route_distribution_id = oci_core_drg_route_distribution.vcp_drg-db_vcn-db_attch_route-import.id  
    display_name = "vcn-db_attch_route-table"    
}

#-----------------------#
# DRG-DB REMOTE-PEERING #
#-----------------------#

# DRG Import Route Distribution
resource "oci_core_drg_route_distribution" "vcp_drg-db_remote-peering_route-import" {
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-db.id
    distribution_type = "IMPORT"
    display_name = "drg-db_remote-peering_route-import"
}

# DRG Import Route Distribution Statements
resource "oci_core_drg_route_distribution_statement" "vcp_drg-db_remote-peering_route-import_statement" {
    provider = oci.vcp

    drg_route_distribution_id = oci_core_drg_route_distribution.vcp_drg-db_remote-peering_route-import.id
    
    action = "ACCEPT"
    priority = 1

    match_criteria {
        match_type = "DRG_ATTACHMENT_TYPE"
        attachment_type = "VCN"                   
    }    
}

# DRG Route Table
resource "oci_core_drg_route_table" "vcp_drg-db_remote-peering_route-table" {  
    provider = oci.vcp

    drg_id = oci_core_drg.vcp_drg-db.id 
    import_drg_route_distribution_id = oci_core_drg_route_distribution.vcp_drg-db_remote-peering_route-import.id
    display_name = "drg-db_remote-peering_route-table"    
}

resource "oci_core_drg_attachment_management" "vcp_drg-db_remote-peering_attch" {
  provider = oci.vcp

  compartment_id = var.compartment_id
  drg_id = oci_core_drg.vcp_drg-db.id
  display_name = "drg-db_remote-peering_attch"

  attachment_type = "REMOTE_PEERING_CONNECTION"  
  network_id = oci_core_remote_peering_connection.vcp_drg-db_remote-peering.id
  drg_route_table_id = oci_core_drg_route_table.vcp_drg-db_remote-peering_route-table.id
}