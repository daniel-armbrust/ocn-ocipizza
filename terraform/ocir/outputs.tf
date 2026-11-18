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
