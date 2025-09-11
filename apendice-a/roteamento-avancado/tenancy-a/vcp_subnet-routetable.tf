#
# vcp_subnet-routetable.tf
#   - Tabelas de Roteamento das sub-redes da região VCP.
#

#--------------#
# vcn-firewall #
#--------------#

# subnprv-lan
resource "oci_core_route_table" "vcp_vcn-firewall_subnprv-lan_route-table" {   
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-firewall.id
    display_name = "subnprv-lan_route-table"

    # DRG-APPL
    route_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_drg.vcp_drg-appl.id
    }

    # Service Gateway
    route_rules {
        destination = "all-vcp-services-in-oracle-services-network"
        destination_type = "SERVICE_CIDR_BLOCK"        
        network_entity_id = oci_core_service_gateway.vcp_vcn-firewall_sgw.id  
    }
}

# subnprv-wan-outbound
resource "oci_core_route_table" "vcp_vcn-firewall_subnprv-wan-outbound_route-table" {   
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-firewall.id
    display_name = "subnprv-wan-outbound_route-table"

    # NAT Gateway
    route_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_nat_gateway.vcp_vcn-firewall_ngw.id
    }    
}

#---------#
# vcn-vpn #
#---------#

# subnpub-1
resource "oci_core_route_table" "vcp_vcn-vpn_subnpub-1_route-table" {   
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-vpn.id
    display_name = "subnpub-vpn_route-table"
    
    # Internet Gateway
    route_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_internet_gateway.vcp_vcn-vpn_igw.id
    }
}

#------------#
# vcn-appl-1 #
#------------#

# subnpub-1
resource "oci_core_route_table" "vcp_vcn-appl-1_subnpub-1_route-table" {   
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-1.id
    display_name = "subnpub-1_route-table"
    
    # DRG-APPL
    route_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_internet_gateway.vcp_vcn-appl-1_igw.id
    } 
}

# subnprv-1
resource "oci_core_route_table" "vcp_vcn-appl-1_subnprv-1_route-table" {   
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-1.id
    display_name = "subnprv-1_route-table"
    
    # DRG-APPL
    route_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_drg.vcp_drg-appl.id
    }

    # VCN-DB (subnprv-1)
    route_rules {
        destination = "172.16.20.128/25"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_local_peering_gateway.vcp_vcn-appl-1_local-peering.id
    } 

    # Service Gateway
    route_rules {
        destination = "all-vcp-services-in-oracle-services-network"
        destination_type = "SERVICE_CIDR_BLOCK"        
        network_entity_id = oci_core_service_gateway.vcp_vcn-appl-1_sgw.id  
    }
}

#------------#
# vcn-appl-2 #
#------------#

# subnprv-1
resource "oci_core_route_table" "vcp_vcn-appl-2_subnprv-1_route-table" {   
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-2.id
    display_name = "subnprv-1_route-table"
    
    # DRG-APPL
    route_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_drg.vcp_drg-appl.id
    }
}

#--------#
# vcn-db #
#--------#

# subnprv-1
resource "oci_core_route_table" "vcp_vcn-db_subnprv-1_route-table" {   
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-db.id
    display_name = "subnprv-1_route-table"
    
    # DRG-DB
    route_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_drg.vcp_drg-db.id
    }

    # VCN-APPL-1 (subnprv-1)
    route_rules {
        destination = "192.168.30.128/25"
        destination_type = "CIDR_BLOCK"
        network_entity_id = oci_core_local_peering_gateway.vcp_vcn-db_local-peering.id
    } 

    # Service Gateway
    route_rules {
        destination = "all-vcp-services-in-oracle-services-network"
        destination_type = "SERVICE_CIDR_BLOCK"        
        network_entity_id = oci_core_service_gateway.vcp_vcn-db_sgw.id  
    }
}