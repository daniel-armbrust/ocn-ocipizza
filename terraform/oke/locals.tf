#
# oke/locals.tf
#

locals {
  # Nomes regionais tornam os recursos facilmente identificáveis na Console.
  cluster_name   = "oke-${var.region_key}"
  node_pool_name = "oke-workers-${var.region_key}"

  # Converte o nome amigável do tipo de cluster no valor esperado pelo OKE.
  cluster_types = {
    BASIC    = "BASIC_CLUSTER"
    ENHANCED = "ENHANCED_CLUSTER"
  }

  # FLANNEL mantém os pods sobre a rede overlay do Kubernetes. Com isso,
  # a VCN-OKE precisa somente das sub-redes já dedicadas ao API, LB e workers.
  cni_type     = "FLANNEL_OVERLAY"
  cluster_type = local.cluster_types[var.cluster_type]

  # Cada worker E4 Flex recebe exatamente 2 OCPUs e 4 GB de RAM.
  node_shape     = "VM.Standard.E4.Flex"
  node_ocpus     = 2
  node_memory_gb = 4
  node_pool_size = 0

  # Caminho do cloud-init aplicado aos worker nodes.
  worker_cloud_init_path = "${path.module}/scripts/oke-cloudinit.sh"

  # Mantém somente imagens oficiais OKE OL8.10 da mesma versão do Kubernetes.
  # Imagens GPU são excluídas porque não são compatíveis com o shape E4 Flex.
  compatible_worker_images = {
    for source in data.oci_containerengine_node_pool_option.this.sources :
    source.source_name => source.image_id
    if source.source_type == "IMAGE"
    && can(regex("Oracle-Linux-8[.]10-.*-OKE-${trimprefix(var.kubernetes_version, "v")}-", source.source_name))
    && !can(regex("GPU", source.source_name))
  }

  compatible_worker_image_names = sort(keys(local.compatible_worker_images))
  selected_worker_image_id = var.worker_image_id != null ? var.worker_image_id : (
    length(local.compatible_worker_image_names) > 0
    ? local.compatible_worker_images[local.compatible_worker_image_names[length(local.compatible_worker_image_names) - 1]]
    : null
  )

}
