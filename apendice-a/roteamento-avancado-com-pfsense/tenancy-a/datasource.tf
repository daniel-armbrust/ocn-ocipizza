#
# datasource.tf
# 

data "oci_core_services" "gru_all_oci_services" {
    provider = oci.gru

    filter {
       name   = "name"
       values = ["All .* Services In Oracle Services Network"]
       regex  = true
    }
}

data "oci_core_services" "vcp_all_oci_services" {
    provider = oci.vcp
  
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

data "oci_identity_availability_domains" "vcp_ads" {
    provider = oci.vcp  
    
    compartment_id = var.tenancy_id
}

data "oci_identity_fault_domains" "gru_fds" {
    provider = oci.gru
    
    compartment_id = var.tenancy_id
    availability_domain = local.ads["gru_ad1_name"]
}

data "oci_identity_fault_domains" "vcp_fds" {
    provider = oci.vcp

    compartment_id = var.tenancy_id
    availability_domain = local.ads["vcp_ad1_name"]
}

#--------------------#
# GRU FIREWALL VNICs #
#--------------------#

data "oci_core_vnic_attachments" "gru_vm_firewall_vnics" {
  provider = oci.gru

  compartment_id = var.compartment_id
  depends_on = [oci_core_instance.gru_vm_firewall]
  instance_id = oci_core_instance.gru_vm_firewall.id
}

data "oci_core_vnic" "gru_vm_firewall_vnic_lan" {
    provider = oci.gru

    depends_on = [oci_core_instance.gru_vm_firewall]
    vnic_id = lookup(data.oci_core_vnic_attachments.gru_vm_firewall_vnics.vnic_attachments[0], "vnic_id")
}

data "oci_core_private_ips" "gru_vm_firewall_vnic_lan_private-ip" {
    provider = oci.gru

    depends_on = [oci_core_instance.gru_vm_firewall]
    vnic_id = data.oci_core_vnic.gru_vm_firewall_vnic_lan.id
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