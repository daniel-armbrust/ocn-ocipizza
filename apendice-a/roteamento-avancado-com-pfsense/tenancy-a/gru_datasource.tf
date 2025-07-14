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

#------------------#
# GRU VCN-FIREWALL #
#------------------#

data "oci_core_subnet" "gru_vcn-firewall_subnprv-lan" {
    provider = oci.gru
    
    subnet_id = oci_core_subnet.gru_vcn-firewall_subnprv-lan.id
}

#----------------#
# GRU VCN-APPL-1 #
#----------------#

data "oci_core_subnet" "gru_vcn-appl-1_subnprv-1" {
    provider = oci.gru
    
    subnet_id = oci_core_subnet.gru_vcn-appl-1_subnprv-1.id
}

#----------------#
# GRU VCN-APPL-2 #
#----------------#

data "oci_core_subnet" "gru_vcn-appl-2_subnprv-1" {
    provider = oci.gru
    
    subnet_id = oci_core_subnet.gru_vcn-appl-2_subnprv-1.id
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