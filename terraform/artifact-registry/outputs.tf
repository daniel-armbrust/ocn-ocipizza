#
# artifact-registry/outputs.tf
#

output "repository_id" {
  description = "OCID do repositório regional de manifests Kubernetes."
  value       = oci_artifacts_repository.kubernetes_manifests.id
}

output "repository_name" {
  description = "Nome do repositório regional de manifests Kubernetes."
  value       = oci_artifacts_repository.kubernetes_manifests.display_name
}
