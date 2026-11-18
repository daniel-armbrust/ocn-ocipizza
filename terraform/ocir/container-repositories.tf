#
# ocir/container-repositories.tf
#

# Repositório privado das imagens do pizza-service. Cada build publica uma tag
# baseada no identificador da execução para distinguir a versão produzida.
resource "oci_artifacts_container_repository" "pizza_service" {
  compartment_id = var.compartment_id
  display_name   = local.pizza_service_repository_name
  is_public      = false
}

# Repositório privado das imagens do user-service. Cada build publica uma tag
# baseada no identificador da execução para distinguir a versão produzida.
resource "oci_artifacts_container_repository" "user_service" {
  compartment_id = var.compartment_id
  display_name   = local.user_service_repository_name
  is_public      = false
}
