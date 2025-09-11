#
# gru_subnet.tf
#   - Sub-redes da região GRU.
#

#--------------#
# vcn-firewall #
#--------------#

# subnprv-lan
resource "oci_core_subnet" "gru_vcn-firewall_subnprv-lan" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-firewall.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-firewall_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-firewall_subnprv-lan_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-firewall_subnprv-lan_secl.id]

    display_name = "subnprv-fw-lan"
    dns_label = "subnprvlan"
    prohibit_public_ip_on_vnic = true

    cidr_block = "10.100.10.0/28"

    ipv6cidr_blocks = [
        "fde3:50e0:8c08:0000::/64"
    ]    
}

# subnprv-wan-outbound
resource "oci_core_subnet" "gru_vcn-firewall_subnprv-wan-outbound" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-firewall.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-firewall_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-firewall_subnprv-wan-outbound_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-firewall_subnprv-wan-outbound_secl.id]

    display_name = "subnprv-fw-wanout"
    dns_label = "subnprvwanout"
    prohibit_public_ip_on_vnic = true

    cidr_block = "10.100.10.32/28" 

    ipv6cidr_blocks = [
        "fde3:50e0:8c08:0001::/64"
    ]    
}

#---------#
# vcn-vpn #
#---------#

# subnpub-vpn
resource "oci_core_subnet" "gru_vcn-vpn_subnpub-1" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-vpn.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-vpn_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-vpn_subnpub-1_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-vpn_subnpub-1_secl.id]

    display_name = "subnpub-vpn"
    dns_label = "subnprvvpn"
    prohibit_public_ip_on_vnic = false

    cidr_block = "10.100.100.0/28"
   
    ipv6cidr_blocks = [
        format("%s%s", replace(join(", ", oci_core_vcn.gru_vcn-vpn.ipv6cidr_blocks), "/56", ""), "/64")
    ]   
}

#------------#
# vcn-appl-1 #
#------------#

# subnpub-1
resource "oci_core_subnet" "gru_vcn-appl-1_subnpub-1" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-appl-1.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-appl-1_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-appl-1_subnpub-1_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-appl-1_subnpub-1_secl.id]

    display_name = "subnpub-1"
    dns_label = "subnpub1"
    prohibit_public_ip_on_vnic = false

    cidr_block = "192.168.10.0/25"

    ipv6cidr_blocks = [
        format("%s%s", replace(join(", ", oci_core_vcn.gru_vcn-appl-1.ipv6cidr_blocks), "/56", ""), "/64")
    ]    
}

# subnprv-1
resource "oci_core_subnet" "gru_vcn-appl-1_subnprv-1" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-appl-1.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-appl-1_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-appl-1_subnprv-1_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-appl-1_subnprv-1_secl.id]

    display_name = "subnprv-1"
    dns_label = "subnprv1"
    prohibit_public_ip_on_vnic = true

    cidr_block = "192.168.10.128/25"

    ipv6cidr_blocks = [
        "fde3:50e0:8c10:0000::/64"
    ] 
}

#------------#
# vcn-appl-2 #
#------------#

# subnprv-1
resource "oci_core_subnet" "gru_vcn-appl-2_subnprv-1" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-appl-2.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-appl-2_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-appl-2_subnprv-1_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-appl-2_subnprv-1_secl.id]

    display_name = "subnprv-1"
    dns_label = "subnprv1"
    prohibit_public_ip_on_vnic = true

    cidr_block = "192.168.20.128/25"

    ipv6cidr_blocks = [
        "fde3:50e0:8c11:0000::/64"
    ]   
}

#--------#
# vcn-db #
#--------#

# subnprv-1
resource "oci_core_subnet" "gru_vcn-db_subnprv-1" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-db.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-db_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-db_subnprv-1_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-db_subnprv-1_secl.id]

    display_name = "subnprv-1"
    dns_label = "subnprv1"
    prohibit_public_ip_on_vnic = true

    cidr_block = "172.16.10.128/25"

    ipv6cidr_blocks = [
        "fde3:50e0:8c12:0000::/64"
    ]   
}