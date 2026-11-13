#
# oke/datasource.tf
#

# OKE exige um Availability Domain para cada placement configuration.
data "oci_identity_availability_domains" "this" {
  compartment_id = var.compartment_id
}

# A lista de opções permite consultar imagens compatíveis com a arquitetura
# x86_64. O usuário pode sobrescrever a imagem por worker_image_id quando quiser
# fixar explicitamente uma imagem regional.
data "oci_containerengine_node_pool_option" "this" {
  compartment_id                 = var.compartment_id
  node_pool_k8s_version          = var.kubernetes_version
  node_pool_option_id            = "all"
  node_pool_os_arch              = "X86_64"
  should_list_all_patch_versions = false
}
