#
# locals.tf
#

locals {
   # My Public IP Address
   my_public_ip = data.external.get_my_public_ip.result.my_public_ip
   
   # IANA protocol numbers
   icmp_protocol = 1
   tcp_protocol = 6
   udp_protocol = 17
   
   # Service Gateway
   gru_all_oci_services = lookup(data.oci_core_services.gru_all_oci_services.services[0], "id")
   gru_oci_services_cidr_block = lookup(data.oci_core_services.gru_all_oci_services.services[0], "cidr_block")   
   vcp_all_oci_services = lookup(data.oci_core_services.vcp_all_oci_services.services[0], "id")
   vcp_oci_services_cidr_block = lookup(data.oci_core_services.vcp_all_oci_services.services[0], "cidr_block")
   
   # Object Storage Namespace
   objectstorage_ns = data.oci_objectstorage_namespace.objectstorage_ns.namespace

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
         "ol96-amd64" = "ocid1.image.oc1.sa-saopaulo-1.aaaaaaaa6xernq3m762v6h5m36t36vvqinj7hbgd77lr2fhbavsqjw2fav5q"
         "ol96-arm" = "ocid1.image.oc1.sa-saopaulo-1.aaaaaaaaeiryb62ld5b2vrzqtf53zt5nbuwiv7d4nxuavggkfza5yjhqpfwa"
      },
      "vcp" = {
         "ol96-amd64" = "ocid1.image.oc1.sa-vinhedo-1.aaaaaaaadfrypyflfastxkcwj676ongsiovxorcxs5hhwdj2isvaqef5dn4q"
         "ol96-arm" = "ocid1.image.oc1.sa-vinhedo-1.aaaaaaaa67iviabbfci4gwtilfxnhdgjyemziltyc2vaeojxyen3nysov7fa"
      }
   }

}