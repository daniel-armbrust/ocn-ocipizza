#
# vcp_gateways.tf
#   - Internet, NAT e Service Gateways da região VCP.
#

#--------------#
# vcn-firewall #
#--------------#

resource "oci_core_nat_gateway" "vcp_vcn-firewall_ngw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-firewall.id
    display_name = "ngw"
    block_traffic = false    
}

resource "oci_core_service_gateway" "vcp_vcn-firewall_sgw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-firewall.id
    display_name = "sgw"

    services {     
        service_id = local.vcp_all_oci_services
    }
}

# resource "oci_core_internet_gateway" "vcp_vcn-firewall_igw" {
#     provider = oci.vcp
    
#     compartment_id = var.compartment_id
#     vcn_id = oci_core_vcn.vcp_vcn-firewall.id    
#     display_name = "igw"    
#     enabled = true   
# }

#------------#
# vcn-appl-1 #
#------------#

resource "oci_core_nat_gateway" "vcp_vcn-appl-1_ngw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-1.id
    display_name = "ngw"
    block_traffic = false    
}

resource "oci_core_service_gateway" "vcp_vcn-appl-1_sgw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-1.id
    display_name = "sgw"

    services {     
        service_id = local.vcp_all_oci_services
    }
}

#------------#
# vcn-appl-2 #
#------------#

resource "oci_core_nat_gateway" "vcp_vcn-appl-2_ngw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-2.id
    display_name = "ngw"
    block_traffic = false    
}

resource "oci_core_service_gateway" "vcp_vcn-appl-2_sgw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-2.id
    display_name = "sgw"

    services {     
        service_id = local.vcp_all_oci_services
    }
}

#--------#
# vcn-db #
#--------#

resource "oci_core_nat_gateway" "vcp_vcn-db_ngw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-db.id
    display_name = "ngw"
    block_traffic = false    
}

resource "oci_core_service_gateway" "vcp_vcn-db_sgw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-db.id
    display_name = "sgw"

    services {     
        service_id = local.vcp_all_oci_services
    }
}

#--------------#
# vcn-internet #
#--------------#

resource "oci_core_internet_gateway" "vcp_vcn-internet_igw" {
    provider = oci.vcp
    
    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-internet.id    
    display_name = "igw"    
    enabled = true   
}