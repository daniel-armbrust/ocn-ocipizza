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

# Repositório privado das imagens do admin-service. Cada build publica uma tag
# baseada no identificador da execução para distinguir a versão produzida.
resource "oci_artifacts_container_repository" "admin_service" {
  compartment_id = var.compartment_id
  display_name   = local.admin_service_repository_name
  is_public      = false
}

# Repositório privado das imagens do chatbot-service. Cada build publica uma
# tag baseada no identificador da execução para distinguir a versão produzida.
resource "oci_artifacts_container_repository" "chatbot_service" {
  compartment_id = var.compartment_id
  display_name   = local.chatbot_service_repository_name
  is_public      = false
}

# Repositório privado das imagens do delivery-service. Cada build publica uma
# tag baseada no identificador da execução para distinguir a versão produzida.
resource "oci_artifacts_container_repository" "delivery_service" {
  compartment_id = var.compartment_id
  display_name   = local.delivery_service_repository_name
  is_public      = false
}

# Repositório privado das imagens do frontend-service. Cada build publica uma
# tag baseada no identificador da execução para distinguir a versão produzida.
resource "oci_artifacts_container_repository" "frontend_service" {
  compartment_id = var.compartment_id
  display_name   = local.frontend_service_repository_name
  is_public      = false
}

# Repositório privado das imagens do notification-service. Cada build publica
# uma tag baseada no identificador da execução para distinguir a versão.
resource "oci_artifacts_container_repository" "notification_service" {
  compartment_id = var.compartment_id
  display_name   = local.notification_service_repository_name
  is_public      = false
}

# Repositório privado das imagens do order-service. Cada build publica uma tag
# baseada no identificador da execução para distinguir a versão produzida.
resource "oci_artifacts_container_repository" "order_service" {
  compartment_id = var.compartment_id
  display_name   = local.order_service_repository_name
  is_public      = false
}
