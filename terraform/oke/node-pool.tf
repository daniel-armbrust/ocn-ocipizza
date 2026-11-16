#
# oke/node-pool.tf
#

resource "oci_containerengine_node_pool" "this" {
  cluster_id         = oci_containerengine_cluster.this.id
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = local.node_pool_name
  node_shape         = local.node_shape

  # Três workers na sub-rede privada exclusiva dos nodes.
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

  # Instala somente o conteúdo da chave pública recebido pelo root module.
  ssh_public_key = var.ssh_public_key

  # O cloud-init personalizado preserva o bootstrap padrão do OKE e aplica as
  # configurações adicionais dos worker nodes.
  node_metadata = {
    # Permite somente o IMDSv2 e desabilita os endpoints legados do IMDSv1.
    areLegacyImdsEndpointsDisabled = "true"
    user_data                      = base64encode(file(local.worker_cloud_init_path))
  }

  # Usa uma imagem oficial OKE OL8.10 compatível com a versão do Kubernetes.
  # Uma imagem específica ainda pode ser fixada por worker_image_id.
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
      error_message = "Não foi encontrada uma imagem oficial OKE OL8.10 compatível com a versão do Kubernetes. Informe worker_image_id."
    }
  }
}
