#
# devops/outputs.tf
#

output "project_id" {
  description = "OCID do projeto OCI DevOps do OCI Pizza."
  value       = oci_devops_project.ocipizza.id
}

output "github_connection_id" {
  description = "OCID da conexão externa do OCI DevOps com o GitHub."
  value       = oci_devops_connection.github_ocipizza.id
}

output "github_repository_url" {
  description = "URL do repositório GitHub espelhado pelo OCI DevOps."
  value       = local.github_repository_url
}

output "mirrored_repository_id" {
  description = "OCID do repositório do OCI DevOps que espelha o GitHub."
  value       = oci_devops_repository.ocipizza.id
}

output "mirrored_repository_http_url" {
  description = "URL HTTP do mirror hospedado no OCI Code Repository."
  value       = oci_devops_repository.ocipizza.http_url
}
