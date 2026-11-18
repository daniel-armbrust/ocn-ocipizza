#
# devops/admin-service/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da build pipeline do admin-service."
  value       = oci_devops_build_pipeline.admin_service.id
}

output "build_stage_id" {
  description = "OCID do Managed Build stage do admin-service."
  value       = oci_devops_build_pipeline_stage.build_admin_service.id
}

output "container_artifact_id" {
  description = "OCID do artefato de imagem do admin-service no OCI DevOps."
  value       = oci_devops_deploy_artifact.admin_service_image.id
}

output "deliver_artifact_stage_id" {
  description = "OCID do stage que publica a imagem do admin-service no OCIR."
  value       = oci_devops_build_pipeline_stage.deliver_admin_service_image.id
}
