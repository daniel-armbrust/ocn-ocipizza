#
# vcp_compute.tf
#   - Maquinas Virtuais da região VCP. 
#

resource "oci_core_instance" "vcp_vm_wordpress-1" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    availability_domain = local.ads.vcp_ad1_name        
    display_name = "vm_wordpress-1"

    shape = "VM.Standard.A1.Flex" 

    shape_config { 
        baseline_ocpu_utilization = "BASELINE_1_1"
        memory_in_gbs = 2
        ocpus = 2
    }

    source_details {
        source_id = local.compute_image_id.vcp.ol96-arm
        source_type = "image"
        boot_volume_size_in_gbs = 100
    }  
    
    metadata = {
        ssh_authorized_keys = file("./sshkeys/firewall-ssh-key.pub")
        user_data = base64encode(file("./scripts/wordpress-init.sh"))
    }

    create_vnic_details {
        display_name = "vnic-1"
        hostname_label = "vcp-wordpress-1"
        private_ip = "192.168.30.130"    
        subnet_id = oci_core_subnet.vcp_vcn-appl-1_subnprv-1.id
        skip_source_dest_check = false
        assign_public_ip = false
        assign_ipv6ip = true
    }   
}

resource "oci_core_instance" "vcp_vm_appl-2" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    availability_domain = local.ads.vcp_ad1_name        
    display_name = "appl-2"

    shape = "VM.Standard.A1.Flex" 

    shape_config { 
        baseline_ocpu_utilization = "BASELINE_1_1"
        memory_in_gbs = 4
        ocpus = 2
    }

    source_details {
        source_id = local.compute_image_id.vcp.ol96-arm
        source_type = "image"
        boot_volume_size_in_gbs = 50
    }  
    
    metadata = {
        ssh_authorized_keys = file("./sshkeys/ssh-key.pub")
        user_data = base64encode(file("./scripts/linux-init.sh"))
    }

    create_vnic_details {
        display_name = "vnic-1"
        hostname_label = "vcp-appl-2"
        private_ip = "192.168.40.140"
        subnet_id = oci_core_subnet.vcp_vcn-appl-2_subnprv-1.id
        skip_source_dest_check = false
        assign_public_ip = false
        assign_ipv6ip = true  
    }   
}