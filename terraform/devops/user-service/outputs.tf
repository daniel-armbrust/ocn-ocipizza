#
# devops/user-service/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da build pipeline do user-service."
  value       = oci_devops_build_pipeline.user_service.id
}

output "build_stage_id" {
  description = "OCID do Managed Build stage do user-service."
  value       = oci_devops_build_pipeline_stage.build_user_service.id
}

output "container_artifact_id" {
  description = "OCID do artefato de imagem do user-service no OCI DevOps."
  value       = oci_devops_deploy_artifact.user_service_image.id
}

output "deliver_artifact_stage_id" {
  description = "OCID do stage que publica a imagem do user-service no OCIR."
  value       = oci_devops_build_pipeline_stage.deliver_user_service_image.id
}
