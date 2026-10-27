#
# oke/node-pool.tf
#

resource "oci_containerengine_node_pool" "this" {
  cluster_id         = oci_containerengine_cluster.this.id
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = local.node_pool_name
  node_shape         = local.node_shape

  # Os três workers são criados na sub-rede privada e distribuídos pelo OKE
  # dentro do Availability Domain selecionado.
  node_config_details {
    placement_configs {
      availability_domain = data.oci_identity_availability_domains.this.availability_domains[0].name
      subnet_id           = var.worker_subnet_id
    }

    size = local.node_pool_size
  }

  node_shape_config {
    memory_in_gbs = local.node_memory_gb
    ocpus         = local.node_ocpus
  }

  # O conteúdo de keys/worker-nodes.pub é instalado nos três worker nodes.
  ssh_public_key = local.worker_ssh_public_key

  dynamic "node_source_details" {
    for_each = local.selected_worker_image_id == null ? [] : [local.selected_worker_image_id]

    content {
      image_id    = node_source_details.value
      source_type = "IMAGE"
    }
  }

  lifecycle {
    precondition {
      condition     = local.worker_ssh_public_key != null && local.worker_ssh_public_key != ""
      error_message = "Gere a chave pública em oke/keys/worker-nodes.pub antes de criar o node pool."
    }

    precondition {
      condition     = local.selected_worker_image_id != null
      error_message = "Não foi encontrada imagem Oracle Linux x86 compatível. Informe worker_image_id."
    }
  }
}
