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
    ipv6private_cidr_blocks = ["fde3:50e0:8d08::/48"]
    is_oracle_gua_allocation_enabled = false

    lifecycle {
        ignore_changes = [
           is_ipv6enabled
        ]
    }
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
    ipv6private_cidr_blocks = ["fde3:50e0:8d09::/48"]
    is_oracle_gua_allocation_enabled = true
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
    ipv6private_cidr_blocks = ["fde3:50e0:8d10::/48"]
    is_oracle_gua_allocation_enabled = true
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
    ipv6private_cidr_blocks = ["fde3:50e0:8d11::/48"]
    is_oracle_gua_allocation_enabled = false

    lifecycle {
        ignore_changes = [
           is_ipv6enabled
        ]
    }
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
    ipv6private_cidr_blocks = ["fde3:50e0:8d12::/48"]
    is_oracle_gua_allocation_enabled = false

    lifecycle {
        ignore_changes = [
           is_ipv6enabled
        ]
    }
}