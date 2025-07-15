#
# vcp_vcn.tf
#   - VCNs da região VCP.
#

#--------------#
# vcn-firewall #
#--------------#

resource "oci_core_vcn" "vcp_vcn-firewall" {    
    provider = oci.vcp

    compartment_id = var.compartment_id
    cidr_blocks = ["10.100.20.0/24"]
    display_name = "vcn-firewall"
    dns_label = "vcpvcnfw"

    # IPv6    
    is_ipv6enabled = true
}

#---------#
# vcn-vpn #
#---------#

resource "oci_core_vcn" "vcp_vcn-vpn" {    
    provider = oci.vcp

    compartment_id = var.compartment_id
    cidr_blocks = ["10.100.200.0/24"]
    display_name = "vcn-vpn"
    dns_label = "vcpvcnvpn"

    # IPv6    
    is_ipv6enabled = true
}

#------------#
# vcn-appl-1 #
#------------#

resource "oci_core_vcn" "vcp_vcn-appl-1" {    
    provider = oci.vcp

    compartment_id = var.compartment_id
    cidr_blocks = ["192.168.30.0/24"]
    display_name = "vcn-appl-1"
    dns_label = "vcpvcnappl1"

    # IPv6    
    is_ipv6enabled = true
}

#------------#
# vcn-appl-2 #
#------------#

resource "oci_core_vcn" "vcp_vcn-appl-2" {    
    provider = oci.vcp

    compartment_id = var.compartment_id
    cidr_blocks = ["192.168.40.0/24"]
    display_name = "vcn-appl-2"
    dns_label = "vcpvcnappl2"

    # IPv6    
    is_ipv6enabled = true
}

#--------#
# vcn-db #
#--------#

resource "oci_core_vcn" "vcp_vcn-db" {    
    provider = oci.vcp

    compartment_id = var.compartment_id
    cidr_blocks = ["172.16.20.0/24"]
    display_name = "vcn-db"
    dns_label = "vcpvcndb"

    # IPv6    
    is_ipv6enabled = true
}

#--------------#
# vcn-internet #
#--------------#

resource "oci_core_vcn" "vcp_vcn-internet" {    
    provider = oci.vcp

    compartment_id = var.compartment_id
    cidr_blocks = ["10.100.60.0/24"]
    display_name = "vcn-internet"
    dns_label = "vcpvcninet"

    # IPv6    
    is_ipv6enabled = true
}
