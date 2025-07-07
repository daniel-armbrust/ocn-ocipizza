#
# locals.tf
#

locals { 
   # IANA protocol numbers
   icmp_protocol = 1
   tcp_protocol = 6
   udp_protocol = 17
   
   # Service Gateway
   gru_all_oci_services = lookup(data.oci_core_services.gru_all_oci_services.services[0], "id")
   gru_oci_services_cidr_block = lookup(data.oci_core_services.gru_all_oci_services.services[0], "cidr_block")   
   vcp_all_oci_services = lookup(data.oci_core_services.vcp_all_oci_services.services[0], "id")
   vcp_oci_services_cidr_block = lookup(data.oci_core_services.vcp_all_oci_services.services[0], "cidr_block")

   ads = {
      gru_ad1_id = data.oci_identity_availability_domains.gru_ads.availability_domains[0].id
      gru_ad1_name = data.oci_identity_availability_domains.gru_ads.availability_domains[0].name

      vcp_ad1_id = data.oci_identity_availability_domains.vcp_ads.availability_domains[0].id
      vcp_ad1_name = data.oci_identity_availability_domains.vcp_ads.availability_domains[0].name
   }

    fds = {
      gru_fd1_id = data.oci_identity_fault_domains.gru_fds.fault_domains[0].id,
      gru_fd1_name = data.oci_identity_fault_domains.gru_fds.fault_domains[0].name,

      gru_fd2_id = data.oci_identity_fault_domains.gru_fds.fault_domains[1].id,
      gru_fd2_name = data.oci_identity_fault_domains.gru_fds.fault_domains[1].name,

      gru_fd3_id = data.oci_identity_fault_domains.gru_fds.fault_domains[2].id,
      gru_fd3_name = data.oci_identity_fault_domains.gru_fds.fault_domains[2].name     

      vcp_fd1_id = data.oci_identity_fault_domains.vcp_fds.fault_domains[0].id,
      vcp_fd1_name = data.oci_identity_fault_domains.vcp_fds.fault_domains[0].name,

      vcp_fd2_id = data.oci_identity_fault_domains.vcp_fds.fault_domains[1].id,
      vcp_fd2_name = data.oci_identity_fault_domains.vcp_fds.fault_domains[1].name,

      vcp_fd3_id = data.oci_identity_fault_domains.vcp_fds.fault_domains[2].id,
      vcp_fd3_name = data.oci_identity_fault_domains.vcp_fds.fault_domains[2].name
   }
}