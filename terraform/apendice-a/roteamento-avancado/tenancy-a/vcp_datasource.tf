#
# vcp_datasource.tf
#   - Data Source da região VCP.
#

data "oci_core_services" "vcp_all_oci_services" {
    provider = oci.vcp
  
    filter {
       name   = "name"
       values = ["All .* Services In Oracle Services Network"]
       regex  = true
    }
}

data "oci_identity_availability_domains" "vcp_ads" {
    provider = oci.vcp  
    
    compartment_id = var.tenancy_id
}

data "oci_identity_fault_domains" "vcp_fds" {
    provider = oci.vcp

    compartment_id = var.tenancy_id
    availability_domain = local.ads["vcp_ad1_name"]
}

#--------------------#
# VCP FIREWALL VNICs #
#--------------------#

data "oci_core_vnic_attachments" "vcp_vm_firewall_vnics" {
  provider = oci.vcp

  compartment_id = var.compartment_id  
  instance_id = oci_core_instance.vcp_vm_firewall.id

  depends_on = [oci_core_instance.vcp_vm_firewall]
}

# VNIC LAN
data "oci_core_vnic" "vcp_vm_firewall_vnic_lan" {
    provider = oci.vcp
    
    vnic_id = lookup(data.oci_core_vnic_attachments.vcp_vm_firewall_vnics.vnic_attachments[0], "vnic_id")

    depends_on = [oci_core_instance.vcp_vm_firewall]
}

# VNIC LAN - PRIVATE IPv4
data "oci_core_private_ips" "vcp_vm_firewall_vnic_lan_private-ip" {
    provider = oci.vcp

    vnic_id = data.oci_core_vnic.vcp_vm_firewall_vnic_lan.id

    depends_on = [oci_core_instance.vcp_vm_firewall]
}

# VNIC LAN - PRIVATE IPv6
data "oci_core_ipv6s" "vcp_vm_firewall_vnic_lan_ipv6s" {
    provider = oci.vcp

    subnet_id = oci_core_subnet.vcp_vcn-firewall_subnprv-lan.id 

    depends_on = [oci_core_instance.vcp_vm_firewall]   
}