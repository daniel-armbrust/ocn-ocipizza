#
# vcp_compute.tf
#   - Maquinas Virtuais da região VCP. 
#

resource "oci_core_instance" "vcp_vm_wordpress-1" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    availability_domain = local.ads.vcp_ad1_name        
    display_name = "vm_wordpress-1"

    shape = "VM.Standard.E4.Flex" 

    shape_config { 
        # Baseline usage is 1/2 of an OCPU.
        baseline_ocpu_utilization = "BASELINE_1_2"
        memory_in_gbs = 2
        ocpus = 2
    }

    source_details {
        source_id = local.compute_image_id.vcp.ol9-amd64
        source_type = "image"
        boot_volume_size_in_gbs = 100
    }  
    
    metadata = {
        ssh_authorized_keys = file("./sshkeys/firewall-ssh-key.pub")
        user_data = base64encode(file("./scripts/wordpress-init.sh"))
    }

    # VNIC LAN
    create_vnic_details {
        display_name = "vnic-1"
        hostname_label = "vcp-wordpress-1"
        private_ip = "192.168.30.130"        
        subnet_id = oci_core_subnet.vcp_vcn-appl-1_subnprv-1.id
        skip_source_dest_check = false
        assign_public_ip = false
    }   
}