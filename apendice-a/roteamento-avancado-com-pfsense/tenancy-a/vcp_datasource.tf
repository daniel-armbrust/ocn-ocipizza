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

#------------------#
# VCP VCN-FIREWALL #
#------------------#

data "oci_core_subnet" "vcp_vcn-firewall_subnprv-lan" {
    provider = oci.vcp
    
    subnet_id = oci_core_subnet.vcp_vcn-firewall_subnprv-lan.id
}

#----------------#
# VCP VCN-APPL-1 #
#----------------#

data "oci_core_subnet" "vcp_vcn-appl-1_subnprv-1" {
    provider = oci.vcp
    
    subnet_id = oci_core_subnet.vcp_vcn-appl-1_subnprv-1.id
}

#----------------#
# VCP VCN-APPL-2 #
#----------------#

data "oci_core_subnet" "vcp_vcn-appl-2_subnprv-1" {
    provider = oci.vcp
    
    subnet_id = oci_core_subnet.vcp_vcn-appl-2_subnprv-1.id
}

#--------------------#
# VCP FIREWALL VNICs #
#--------------------#

data "oci_core_vnic_attachments" "vcp_vm_firewall_vnics" {
  provider = oci.vcp

  compartment_id = var.compartment_id
  depends_on = [oci_core_instance.vcp_vm_firewall]
  instance_id = oci_core_instance.vcp_vm_firewall.id
}

data "oci_core_vnic" "vcp_vm_firewall_vnic_lan" {
    provider = oci.vcp

    depends_on = [oci_core_instance.vcp_vm_firewall]
    vnic_id = lookup(data.oci_core_vnic_attachments.vcp_vm_firewall_vnics.vnic_attachments[0], "vnic_id")
}

data "oci_core_private_ips" "vcp_vm_firewall_vnic_lan_private-ip" {
    provider = oci.vcp

    depends_on = [oci_core_instance.vcp_vm_firewall]
    vnic_id = data.oci_core_vnic.vcp_vm_firewall_vnic_lan.id
}