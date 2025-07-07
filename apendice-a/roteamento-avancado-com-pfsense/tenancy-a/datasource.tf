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