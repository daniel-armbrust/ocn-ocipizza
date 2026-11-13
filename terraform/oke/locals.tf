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
  node_pool_size = 3

  # Caminho do cloud-init aplicado aos worker nodes.
  worker_cloud_init_path = "${path.module}/scripts/oke-cloudinit.sh"

  # Somente a chave pública é enviada ao metadata dos worker nodes.
  worker_ssh_public_key = file("${path.module}/keys/worker-nodes.pub")

  # O filtro x86_64 + Oracle Linux evita selecionar uma imagem ARM ou de outro
  # sistema operacional quando o OCI retornar várias opções.
  compatible_worker_images = sort([
    for source in data.oci_containerengine_node_pool_option.this.sources : source.image_id
    if source.source_type == "IMAGE" && can(regex("Oracle[- ]Linux", source.source_name))
  ])

  # Se o operador não fixar uma imagem, usa a última imagem Oracle Linux x86_64
  # retornada pelo OCI para a versão do Kubernetes escolhida.
  selected_worker_image_id = var.worker_image_id != null ? var.worker_image_id : (
    length(local.compatible_worker_images) > 0 ? local.compatible_worker_images[length(local.compatible_worker_images) - 1] : null
  )
}
