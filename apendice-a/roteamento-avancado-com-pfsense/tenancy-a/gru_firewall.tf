#
# gru_firewall.tf
#   - Firewall da região GRU. 
#

#----------#
# FIREWALL #
#----------#

resource "oci_core_instance" "gru_vm_firewall" {
    provider = oci.gru

    compartment_id = var.compartment_id
    availability_domain = local.ads.gru_ad1_name        
    display_name = "firewall"

    shape = "VM.Standard.E4.Flex" 

    shape_config {
        # Baseline usage is an entire OCPU. 
        # This represents a non-burstable instance. 
        baseline_ocpu_utilization = "BASELINE_1_1"
        memory_in_gbs = 4
        ocpus = 3
    }

    source_details {
        source_id = local.compute_image_id.gru.ol9-amd64
        source_type = "image"
        boot_volume_size_in_gbs = 100
    }  

    agent_config {
        is_management_disabled = false
        is_monitoring_disabled = false

        plugins_config {
            desired_state = "ENABLED"
            name = "Bastion"
        }
    }

    metadata = {
        ssh_authorized_keys = file("./sshkeys/firewall-ssh-key.pub")
        user_data = base64encode(file("./scripts/firewall-init.sh"))
    }

    # VNIC LAN
    create_vnic_details {
        display_name = "vnic_lan"
        hostname_label = "gru-fw"
        private_ip = "10.100.10.14"        
        subnet_id = oci_core_subnet.gru_vcn-firewall_subnprv-lan.id
        skip_source_dest_check = true
        assign_public_ip = false
    }   
}

# VNIC WAN-OUTBOUND
resource "oci_core_vnic_attachment" "gru_vm-firewall_vnic_wan-outbound" {  
    provider = oci.gru

    display_name = "vnic_wan-outbound"
    instance_id = oci_core_instance.gru_vm_firewall.id
    
    create_vnic_details {    
        display_name = "vnic_wan-outbound"    
        hostname_label = "gru-fw-wout"
        private_ip = "10.100.10.46"        
        subnet_id = oci_core_subnet.gru_vcn-firewall_subnprv-wan-outbound.id
        skip_source_dest_check = false
        assign_public_ip = false
    }
}

# VNIC WAN-INBOUND
resource "oci_core_vnic_attachment" "gru_vm-firewall_vnic_wan-inbound" {    
    provider = oci.gru

    display_name = "vnic_wan-inbound"
    instance_id = oci_core_instance.gru_vm_firewall.id
    
    create_vnic_details {    
        display_name = "vnic_wan-inbound"    
        hostname_label = "gru-fw-win"
        private_ip = "10.100.50.254"        
        subnet_id = oci_core_subnet.gru_vcn-internet_subnpub-1.id
        skip_source_dest_check = false
        assign_public_ip = true
    }
}    