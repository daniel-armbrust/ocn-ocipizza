#
# compute-firewall/instance.tf
#

# A única VNIC é criada na sub-rede privada do firewall.
resource "oci_core_instance" "this" {
  availability_domain = data.oci_identity_availability_domains.this.availability_domains[0].name
  compartment_id      = var.compartment_id
  display_name        = local.resource_names.instance
  shape               = local.shape.name

  shape_config {
    ocpus         = local.shape.ocpus
    memory_in_gbs = local.shape.memory_in_gbs
  }

  source_details {
    source_type = "image"
    source_id   = local.config.image_id
  }

  # Habilita o plugin usado pelo OCI Bastion Service para sessões SSH.
  agent_config {
    are_all_plugins_disabled = false
    is_management_disabled   = false
    is_monitoring_disabled   = false

    plugins_config {
      name          = "Bastion"
      desired_state = "ENABLED"
    }
  }

  create_vnic_details {
    display_name              = local.vnic_names.firewall.display_name
    subnet_id                 = var.subnet_ids.firewall
    assign_public_ip          = false
    assign_private_dns_record = true
    hostname_label            = local.vnic_names.firewall.hostname_label

    # O firewall encaminha tráfego de saída para o NAT Gateway.
    skip_source_dest_check = true
  }

  metadata = merge(
    var.ssh_public_key == null ? {} : {
      ssh_authorized_keys = var.ssh_public_key
    },
    {
      # O cloud-init executa o script de preparação do firewall no primeiro boot.
      user_data = base64encode(file("${path.module}/scripts/configure-firewall.sh"))
    }
  )
}
