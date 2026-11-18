#
# ocir/outputs.tf
#

output "pizza_service_repository_id" {
  description = "OCID do repositório de imagens do pizza-service no OCIR."
  value       = oci_artifacts_container_repository.pizza_service.id
}

output "pizza_service_repository_name" {
  description = "Nome do repositório de imagens do pizza-service no OCIR."
  value       = oci_artifacts_container_repository.pizza_service.display_name
}

output "pizza_service_repository_namespace" {
  description = "Namespace da tenancy usado no caminho do repositório do pizza-service."
  value       = oci_artifacts_container_repository.pizza_service.namespace
}

output "pizza_service_repository_url" {
  description = "URL completa do repositório do pizza-service no OCIR, sem tag."
  value       = "${var.region_key}.ocir.io/${oci_artifacts_container_repository.pizza_service.namespace}/${oci_artifacts_container_repository.pizza_service.display_name}"
}

output "user_service_repository_id" {
  description = "OCID do repositório de imagens do user-service no OCIR."
  value       = oci_artifacts_container_repository.user_service.id
}

output "user_service_repository_name" {
  description = "Nome do repositório de imagens do user-service no OCIR."
  value       = oci_artifacts_container_repository.user_service.display_name
}

output "user_service_repository_url" {
  description = "URL completa do repositório do user-service no OCIR, sem tag."
  value       = "${var.region_key}.ocir.io/${oci_artifacts_container_repository.user_service.namespace}/${oci_artifacts_container_repository.user_service.display_name}"
}

output "admin_service_repository_id" {
  description = "OCID do repositório de imagens do admin-service no OCIR."
  value       = oci_artifacts_container_repository.admin_service.id
}

output "admin_service_repository_name" {
  description = "Nome do repositório de imagens do admin-service no OCIR."
  value       = oci_artifacts_container_repository.admin_service.display_name
}

output "admin_service_repository_url" {
  description = "URL completa do repositório do admin-service no OCIR, sem tag."
  value       = "${var.region_key}.ocir.io/${oci_artifacts_container_repository.admin_service.namespace}/${oci_artifacts_container_repository.admin_service.display_name}"
}

output "chatbot_service_repository_id" {
  description = "OCID do repositório de imagens do chatbot-service no OCIR."
  value       = oci_artifacts_container_repository.chatbot_service.id
}

output "chatbot_service_repository_name" {
  description = "Nome do repositório de imagens do chatbot-service no OCIR."
  value       = oci_artifacts_container_repository.chatbot_service.display_name
}

output "chatbot_service_repository_url" {
  description = "URL completa do repositório do chatbot-service no OCIR, sem tag."
  value       = "${var.region_key}.ocir.io/${oci_artifacts_container_repository.chatbot_service.namespace}/${oci_artifacts_container_repository.chatbot_service.display_name}"
}

output "delivery_service_repository_id" {
  description = "OCID do repositório de imagens do delivery-service no OCIR."
  value       = oci_artifacts_container_repository.delivery_service.id
}

output "delivery_service_repository_name" {
  description = "Nome do repositório de imagens do delivery-service no OCIR."
  value       = oci_artifacts_container_repository.delivery_service.display_name
}

output "delivery_service_repository_url" {
  description = "URL completa do repositório do delivery-service no OCIR, sem tag."
  value       = "${var.region_key}.ocir.io/${oci_artifacts_container_repository.delivery_service.namespace}/${oci_artifacts_container_repository.delivery_service.display_name}"
}

output "frontend_service_repository_id" {
  description = "OCID do repositório de imagens do frontend-service no OCIR."
  value       = oci_artifacts_container_repository.frontend_service.id
}

output "frontend_service_repository_name" {
  description = "Nome do repositório de imagens do frontend-service no OCIR."
  value       = oci_artifacts_container_repository.frontend_service.display_name
}

output "frontend_service_repository_url" {
  description = "URL completa do repositório do frontend-service no OCIR, sem tag."
  value       = "${var.region_key}.ocir.io/${oci_artifacts_container_repository.frontend_service.namespace}/${oci_artifacts_container_repository.frontend_service.display_name}"
}

output "notification_service_repository_id" {
  description = "OCID do repositório de imagens do notification-service no OCIR."
  value       = oci_artifacts_container_repository.notification_service.id
}

output "notification_service_repository_name" {
  description = "Nome do repositório de imagens do notification-service no OCIR."
  value       = oci_artifacts_container_repository.notification_service.display_name
}

output "notification_service_repository_url" {
  description = "URL completa do repositório do notification-service no OCIR, sem tag."
  value       = "${var.region_key}.ocir.io/${oci_artifacts_container_repository.notification_service.namespace}/${oci_artifacts_container_repository.notification_service.display_name}"
}

output "order_service_repository_id" {
  description = "OCID do repositório de imagens do order-service no OCIR."
  value       = oci_artifacts_container_repository.order_service.id
}

output "order_service_repository_name" {
  description = "Nome do repositório de imagens do order-service no OCIR."
  value       = oci_artifacts_container_repository.order_service.display_name
}

output "order_service_repository_url" {
  description = "URL completa do repositório do order-service no OCIR, sem tag."
  value       = "${var.region_key}.ocir.io/${oci_artifacts_container_repository.order_service.namespace}/${oci_artifacts_container_repository.order_service.display_name}"
}
