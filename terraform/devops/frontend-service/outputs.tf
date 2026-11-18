#
# devops/frontend-service/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da build pipeline do frontend-service."
  value       = oci_devops_build_pipeline.frontend_service.id
}

output "build_stage_id" {
  description = "OCID do Managed Build stage do frontend-service."
  value       = oci_devops_build_pipeline_stage.build_frontend_service.id
}

output "container_artifact_id" {
  description = "OCID do artefato de imagem do frontend-service no OCI DevOps."
  value       = oci_devops_deploy_artifact.frontend_service_image.id
}

output "deliver_artifact_stage_id" {
  description = "OCID do stage que publica a imagem do frontend-service no OCIR."
  value       = oci_devops_build_pipeline_stage.deliver_frontend_service_image.id
}
