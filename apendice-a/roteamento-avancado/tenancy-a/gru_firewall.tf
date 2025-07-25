#
# gru_firewall.tf
#   - Firewall da região GRU. 
#

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

    extended_metadata = {       
       "primary-vnic-ip" = "10.100.10.14"
       "wan-outbound-ip" = "10.100.10.46"
       "wan-outbound-gw" = "10.100.10.33"
       "wan-vpn-ip" = "10.100.100.14"
       "wan-vpn-gw" = "10.100.100.1"
       "vcp-vcn-firewall-cidr" = "10.100.20.0/24"       
       "gru-vcn-appl-1-cidr" = "192.168.10.0/24"
       "gru-vcn-appl-2-cidr" = "192.168.20.0/24"      
       "vcp-vcn-appl-1-cidr" = "192.168.30.0/24"
       "vcp-vcn-appl-2-cidr" = "192.168.40.0/24"
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
        skip_source_dest_check = true
        assign_public_ip = false
    }    

    depends_on = [oci_core_instance.gru_vm_firewall]   
}

# VNIC WAN-VPN
resource "oci_core_vnic_attachment" "gru_vm-firewall_vnic_wan-vpn" {    
    provider = oci.gru

    display_name = "vnic_wan-vpn"
    instance_id = oci_core_instance.gru_vm_firewall.id
      
    create_vnic_details {    
        display_name = "vnic_wan-vpn"    
        hostname_label = "gru-fw-wvpn"
        private_ip = "10.100.100.14"        
        subnet_id = oci_core_subnet.gru_vcn-vpn_subnpub-1.id
        skip_source_dest_check = true
        assign_public_ip = true
    }    

    depends_on = [oci_core_vnic_attachment.gru_vm-firewall_vnic_wan-outbound] 
}    