#
# oke/datasource.tf
#

# O node pool requer ao menos um Availability Domain em sua configuração de
# placement. O primeiro AD disponível é suficiente para este laboratório.
data "oci_identity_availability_domains" "this" {
  compartment_id = var.compartment_id
}

# Consulta as imagens de worker compatíveis com Kubernetes e arquitetura x86.
data "oci_containerengine_node_pool_option" "this" {
  node_pool_k8s_version          = var.kubernetes_version
  node_pool_option_id            = "all"
  node_pool_os_arch              = "X86_64"
  should_list_all_patch_versions = true
}

locals {
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
