#
# oke/node-pool.tf
#

resource "oci_containerengine_node_pool" "this" {
  cluster_id         = oci_containerengine_cluster.this.id
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = local.node_pool_name
  node_shape         = local.node_shape

  # Dois workers na sub-rede privada exclusiva dos nodes.
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

  # A chave é opcional; quando informada, permite acesso SSH administrativo
  # aos worker nodes sem alterar o funcionamento do cluster.
  ssh_public_key = var.ssh_public_key

  # O image_id é consultado no catálogo de opções do OKE para garantir ARM.
  # O precondition produz uma mensagem clara se não houver imagem compatível.
  dynamic "node_source_details" {
    for_each = local.selected_worker_image_id == null ? [] : [local.selected_worker_image_id]

    content {
      image_id    = node_source_details.value
      source_type = "IMAGE"
    }
  }

  lifecycle {
    precondition {
      condition     = local.selected_worker_image_id != null
      error_message = "Não foi encontrada imagem ARM Oracle Linux compatível para os worker nodes. Informe worker_image_id."
    }
  }
}
