#
# ocir/container-repositories.tf
#

# Repositório privado das imagens do pizza-service. Cada build deve publicar
# uma tag baseada no hash do commit para identificar a versão produzida.
resource "oci_artifacts_container_repository" "pizza_service" {
  compartment_id = var.compartment_id
  display_name   = local.pizza_service_repository_name
  is_public      = false
}
