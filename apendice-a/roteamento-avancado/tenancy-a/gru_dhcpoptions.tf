#
# gru_dhcpoptions.tf
#   - DHCP Options das sub-redes da região GRU.
#

#--------------#
# vcn-firewall #
#--------------#

resource "oci_core_dhcp_options" "gru_vcn-firewall_dhcp-options" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-firewall.id
    display_name = "vcn-firewall_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet" 
    }    
}

#---------#
# vcn-vpn #
#---------#

resource "oci_core_dhcp_options" "gru_vcn-vpn_dhcp-options" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-vpn.id
    display_name = "vcn-vpn_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}

#------------#
# vcn-appl-1 #
#------------#

resource "oci_core_dhcp_options" "gru_vcn-appl-1_dhcp-options" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-appl-1.id
    display_name = "vcn-appl-1_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}

#------------#
# vcn-appl-2 #
#------------#

resource "oci_core_dhcp_options" "gru_vcn-appl-2_dhcp-options" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-appl-2.id
    display_name = "vcn-appl-2_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}

#--------#
# vcn-db #
#--------#

resource "oci_core_dhcp_options" "gru_vcn-db_dhcp-options" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-db.id
    display_name = "vcn-db_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}