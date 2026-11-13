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
