#
# vcp_dhcpoptions.tf
#   - DHCP Options das sub-redes da região VCP.
#

#--------------#
# vcn-firewall #
#--------------#

resource "oci_core_dhcp_options" "vcp_vcn-firewall_dhcp-options" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-firewall.id
    display_name = "vcn-firewall_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}

#---------#
# vcn-vpn #
#---------#

resource "oci_core_dhcp_options" "vcp_vcn-vpn_dhcp-options" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-vpn.id
    display_name = "vcn-vpn_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}

#------------#
# vcn-appl-1 #
#------------#

resource "oci_core_dhcp_options" "vcp_vcn-appl-1_dhcp-options" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-1.id
    display_name = "vcn-appl-1_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}

#------------#
# vcn-appl-2 #
#------------#

resource "oci_core_dhcp_options" "vcp_vcn-appl-2_dhcp-options" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-2.id
    display_name = "vcn-appl-2_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}

#--------#
# vcn-db #
#--------#

resource "oci_core_dhcp_options" "vcp_vcn-db_dhcp-options" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-db.id
    display_name = "vcn-db_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}

#--------------#
# vcn-internet #
#--------------#

resource "oci_core_dhcp_options" "vcp_vcn-internet_dhcp-options" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-internet.id
    display_name = "vcn-internet_dhcp-options"
    
    options {
        type = "DomainNameServer"
        server_type = "VcnLocalPlusInternet"
    }    
}