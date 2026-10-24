#
# oke/datasource.tf
#

# OKE exige um Availability Domain para cada placement configuration.
data "oci_identity_availability_domains" "this" {
  compartment_id = var.compartment_id
}

# A lista de opções permite consultar imagens compatíveis com a arquitetura
# ARM. O usuário pode sobrescrever a imagem por worker_image_id quando quiser
# fixar explicitamente uma imagem regional.
data "oci_containerengine_node_pool_option" "this" {
  compartment_id                 = var.compartment_id
  node_pool_k8s_version          = var.kubernetes_version
  node_pool_option_id            = "all"
  node_pool_os_arch              = "AARCH64"
  should_list_all_patch_versions = false
}

locals {
  # O filtro ARM + Oracle Linux evita selecionar uma imagem x86 ou de outro
  # sistema operacional quando o OCI retornar várias opções.
  compatible_worker_images = sort([
    for source in data.oci_containerengine_node_pool_option.this.sources : source.image_id
    if source.source_type == "IMAGE" && can(regex("Oracle[- ]Linux", source.source_name))
  ])

  # Se o operador não fixar uma imagem, usa a última imagem Oracle Linux ARM
  # retornada pelo OCI para a versão do Kubernetes escolhida.
  selected_worker_image_id = var.worker_image_id != null ? var.worker_image_id : (
    length(local.compatible_worker_images) > 0 ? local.compatible_worker_images[length(local.compatible_worker_images) - 1] : null
  )
}
