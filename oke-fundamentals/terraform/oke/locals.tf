#
# oke/locals.tf
#

locals {
  cluster_name   = "oke-fundamentals"
  node_pool_name = "oke-fundamentals-workers"

  # Caminho do cloud-init aplicado aos worker nodes.
  worker_cloud_init_path = "${path.module}/scripts/oke-cloudinit.sh"

  # Somente a chave pública é lida pelo Terraform e enviada ao OKE. O par de
  # chaves permanece local no diretório keys e não deve ser versionado.
  worker_ssh_public_key_path = "${path.module}/keys/worker-nodes.pub"
  worker_ssh_public_key = fileexists(local.worker_ssh_public_key_path) ? trimspace(
    file(local.worker_ssh_public_key_path)
  ) : null

  # Converte o nome amigável do tipo de cluster no valor esperado pelo OKE.
  cluster_types = {
    BASIC    = "BASIC_CLUSTER"
    ENHANCED = "ENHANCED_CLUSTER"
  }

  # O tipo de CNI já utiliza diretamente o valor esperado pela API do OKE.
  cni_type     = var.cni_type
  cluster_type = local.cluster_types[var.cluster_type]

  # Configuração didática dos três worker nodes x86 AMD.
  node_shape     = "VM.Standard.E4.Flex"
  node_ocpus     = 2
  node_memory_gb = 4
  node_pool_size = 3

  # Mantém somente imagens Oracle Linux x86 de uso geral. As variantes GPU são
  # publicadas na mesma consulta, mas não são compatíveis com o shape E4.Flex.
  compatible_worker_images = {
    for source in coalesce(data.oci_containerengine_node_pool_option.this.sources, []) :
    source.source_name => source.image_id
    if(
      source.source_type == "IMAGE"
      && can(regex("Oracle[- ]Linux", source.source_name))
      && !can(regex("GPU", source.source_name))
    )
  }

  # A ordenação pelo nome, em vez do OCID, torna a escolha determinística e
  # prioriza a versão mais recente dentre as imagens padrão retornadas.
  compatible_worker_image_names = sort(keys(local.compatible_worker_images))

  # Permite fixar um OCID para reproduzir o laboratório. Sem override, utiliza
  # a imagem Oracle Linux x86 mais recente retornada para a versão escolhida.
  selected_worker_image_id = var.worker_image_id != null ? var.worker_image_id : (
    length(local.compatible_worker_image_names) > 0
    ? local.compatible_worker_images[local.compatible_worker_image_names[length(local.compatible_worker_image_names) - 1]]
    : null
  )
}
