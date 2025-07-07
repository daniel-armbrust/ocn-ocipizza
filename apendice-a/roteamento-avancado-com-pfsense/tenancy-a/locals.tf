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

   #
   # See: https://docs.oracle.com/en-us/iaas/images/
   #
   compute_image_id = {
      "gru" = {
         "ol9-amd64" = "ocid1.image.oc1.sa-saopaulo-1.aaaaaaaanvwztmp6itiny5bbua4fdbnfocpkro77r45nymjo7ooqs3oi7f5q"
         "ol9-arm" = "ocid1.image.oc1.sa-saopaulo-1.aaaaaaaath3bwke2i3zu3sgxrgnsboacjihmylxbuogivbgma476pzykarpa"
      },
      "vcp" = {
         "ol9-amd64" = "ocid1.image.oc1.sa-vinhedo-1.aaaaaaaaw664rptgtzyd33ztbzy3vp6twed5w4s62snxq36r53pzelkjwhpq"
         "ol9-arm" = "ocid1.image.oc1.sa-vinhedo-1.aaaaaaaaf6rmi6nbizybqkwg65iuemtmuppyoxnfb2fzfu4le6gngkohtbvq"
      }
   }

}