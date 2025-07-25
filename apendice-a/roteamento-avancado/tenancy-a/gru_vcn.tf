#
# gru_vcn.tf
#   - VCNs da região GRU.
#

#--------------#
# vcn-firewall #
#--------------#

resource "oci_core_vcn" "gru_vcn-firewall" {    
    provider = oci.gru

    compartment_id = var.compartment_id
    cidr_blocks = ["10.100.10.0/24"]
    display_name = "vcn-firewall"
    dns_label = "gruvcnfw"

    # IPv6    
    is_ipv6enabled = true
}

#---------#
# vcn-vpn #
#---------#

resource "oci_core_vcn" "gru_vcn-vpn" {    
    provider = oci.gru

    compartment_id = var.compartment_id
    cidr_blocks = ["10.100.100.0/24"]
    display_name = "vcn-vpn"
    dns_label = "gruvcnvpn"

    # IPv6    
    is_ipv6enabled = true
}

#------------#
# vcn-appl-1 #
#------------#

resource "oci_core_vcn" "gru_vcn-appl-1" {    
    provider = oci.gru

    compartment_id = var.compartment_id
    cidr_blocks = ["192.168.10.0/24"]
    display_name = "vcn-appl-1"
    dns_label = "gruvcnappl1"

    # IPv6    
    is_ipv6enabled = true
}

#------------#
# vcn-appl-2 #
#------------#

resource "oci_core_vcn" "gru_vcn-appl-2" {    
    provider = oci.gru

    compartment_id = var.compartment_id
    cidr_blocks = ["192.168.20.0/24"]
    display_name = "vcn-appl-2"
    dns_label = "gruvcnappl2"

    # IPv6    
    is_ipv6enabled = true
}

#--------#
# vcn-db #
#--------#

resource "oci_core_vcn" "gru_vcn-db" {    
    provider = oci.gru

    compartment_id = var.compartment_id
    cidr_blocks = ["172.16.10.0/24"]
    display_name = "vcn-db"
    dns_label = "gruvcndb"

    # IPv6    
    is_ipv6enabled = true
}