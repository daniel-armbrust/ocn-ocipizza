#
# vcp_subnet-security.tf
#   - Security Lists das sub-redes da região GRU.
#

#--------------#
# vcn-firewall #
#--------------#

# subnprv-lan
resource "oci_core_security_list" "vcp_vcn-firewall_subnprv-lan_secl" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-firewall.id
    display_name = "subnprv-lan_secl"

    egress_security_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        protocol = "all"
        stateless = true
    }

    ingress_security_rules {
        source = "0.0.0.0/0"
        protocol = "all"
        source_type = "CIDR_BLOCK"
        stateless = true
    }
}

# subnprv-wan-outbound
resource "oci_core_security_list" "vcp_vcn-firewall_subnprv-wan-outbound_secl" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-firewall.id
    display_name = "subnprv-wan-outbound_secl"
   
    egress_security_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        protocol = "all"
        stateless = true
    } 

    ingress_security_rules {
        source = "0.0.0.0/0"
        protocol = "all"
        source_type = "CIDR_BLOCK"
        stateless = true
    }   
}

#---------#
# vcn-vpn #
#---------#

resource "oci_core_security_list" "vcp_vcn-vpn_subnpub-1_secl" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-vpn.id
    display_name = "subnpub-vpn_secl"
   
    # egress_security_rules {
    #     destination = "0.0.0.0/0"
    #     destination_type = "CIDR_BLOCK"
    #     protocol = "all"
    #     stateless = true
    # }
        
    ingress_security_rules {
        source = "0.0.0.0/0"
        protocol = "all"
        source_type = "CIDR_BLOCK"
        stateless = true
    }
}

#------------#
# vcn-appl-1 #
#------------#

# subnprv-1
resource "oci_core_security_list" "vcp_vcn-appl-1_subnprv-1_secl" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-1.id
    display_name = "subnprv-1_secl"

    ingress_security_rules {
        source = "0.0.0.0/0"
        protocol = "all"
        source_type = "CIDR_BLOCK"
        stateless = false
    }  

    egress_security_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        protocol = "all"
        stateless = false
    }     
}

#------------#
# vcn-appl-2 #
#------------#

# subnprv-1
resource "oci_core_security_list" "vcp_vcn-appl-2_subnprv-1_secl" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-appl-2.id
    display_name = "subnprv-1_secl"

    ingress_security_rules {
        source = "0.0.0.0/0"
        protocol = "all"
        source_type = "CIDR_BLOCK"
        stateless = false
    }

    egress_security_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        protocol = "all"
        stateless = false
    }    
}

#--------#
# vcn-db #
#--------#

# subnprv-1
resource "oci_core_security_list" "vcp_vcn-db_subnprv-1_secl" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    vcn_id = oci_core_vcn.vcp_vcn-db.id
    display_name = "subnprv-1_secl"

    ingress_security_rules {
        source = "0.0.0.0/0"
        protocol = "all"
        source_type = "CIDR_BLOCK"
        stateless = false
    }

    egress_security_rules {
        destination = "0.0.0.0/0"
        destination_type = "CIDR_BLOCK"
        protocol = "all"
        stateless = false
    }    
}