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

    display_name = "subnprv-lan"
    dns_label = "subnprvlan"
    cidr_block = "10.100.10.0/28"
    prohibit_public_ip_on_vnic = true
}

# subnprv-wan-outbound
resource "oci_core_subnet" "gru_vcn-firewall_subnprv-wan-outbound" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-firewall.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-firewall_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-firewall_subnprv-wan-outbound_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-firewall_subnprv-wan-outbound_secl.id]

    display_name = "subnprv-wan-outbound"
    dns_label = "subnprvwanout"
    cidr_block = "10.100.10.32/28"
    prohibit_public_ip_on_vnic = true
}

# subnprv-wan-inbound
resource "oci_core_subnet" "gru_vcn-firewall_subnpub-wan-inbound" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-firewall.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-firewall_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-firewall_subnpub-wan-inbound_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-firewall_subnpub-wan-inbound_secl.id]

    display_name = "subnpub-wan-inbound"
    dns_label = "subnpubwanin"
    cidr_block = "10.100.10.80/28"
    prohibit_public_ip_on_vnic = false
}

#------------#
# vcn-appl-1 #
#------------#

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
    cidr_block = "192.168.10.128/25"
    prohibit_public_ip_on_vnic = true
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
    cidr_block = "192.168.20.128/25"
    prohibit_public_ip_on_vnic = true
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
    cidr_block = "172.16.10.128/25"
    prohibit_public_ip_on_vnic = true
}

#--------------#
# vcn-internet #
#--------------#

# subnpub-1
resource "oci_core_subnet" "gru_vcn-internet_subnpub-1" {
    provider = oci.gru

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.gru_vcn-internet.id
    dhcp_options_id = oci_core_dhcp_options.gru_vcn-internet_dhcp-options.id
    route_table_id = oci_core_route_table.gru_vcn-internet_subnpub-1_route-table.id
    security_list_ids = [oci_core_security_list.gru_vcn-internet_subnpub-1_secl.id]

    display_name = "subnpub-1"
    dns_label = "subnprv1"
    cidr_block = "10.100.50.128/25"
    prohibit_public_ip_on_vnic = false
}