#
# gru_datasource.tf
#   - Data Source da região GRU.
# 

data "oci_core_services" "gru_all_oci_services" {
    provider = oci.gru

    filter {
       name   = "name"
       values = ["All .* Services In Oracle Services Network"]
       regex  = true
    }
}

data "oci_identity_availability_domains" "gru_ads" {
    provider = oci.gru
    
    compartment_id = var.tenancy_id
}

data "oci_identity_fault_domains" "gru_fds" {
    provider = oci.gru
    
    compartment_id = var.tenancy_id
    availability_domain = local.ads["gru_ad1_name"]
}

#--------------------#
# GRU FIREWALL VNICs #
#--------------------#

data "oci_core_vnic_attachments" "gru_vm_firewall_vnics" {
  provider = oci.gru

  compartment_id = var.compartment_id
  instance_id = oci_core_instance.gru_vm_firewall.id

  depends_on = [oci_core_instance.gru_vm_firewall]
}

# VNIC LAN
data "oci_core_vnic" "gru_vm_firewall_vnic_lan" {
    provider = oci.gru
    
    vnic_id = lookup(data.oci_core_vnic_attachments.gru_vm_firewall_vnics.vnic_attachments[0], "vnic_id")

    depends_on = [oci_core_instance.gru_vm_firewall]
}

# VNIC LAN - PRIVATE IPv4
data "oci_core_private_ips" "gru_vm_firewall_vnic_lan_private-ip" {
    provider = oci.gru
    
    vnic_id = data.oci_core_vnic.gru_vm_firewall_vnic_lan.id

    depends_on = [oci_core_instance.gru_vm_firewall]
}

# VNIC LAN - PRIVATE IPv6
data "oci_core_ipv6s" "gru_vm_firewall_vnic_lan_ipv6s" {
    provider = oci.gru

    subnet_id = oci_core_subnet.gru_vcn-firewall_subnprv-lan.id 

    depends_on = [oci_core_instance.gru_vm_firewall]   
}