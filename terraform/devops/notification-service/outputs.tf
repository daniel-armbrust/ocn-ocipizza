#
# devops/notification-service/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da build pipeline do notification-service."
  value       = oci_devops_build_pipeline.notification_service.id
}

output "build_stage_id" {
  description = "OCID do Managed Build stage do notification-service."
  value       = oci_devops_build_pipeline_stage.build_notification_service.id
}

output "container_artifact_id" {
  description = "OCID do artefato de imagem do notification-service no OCI DevOps."
  value       = oci_devops_deploy_artifact.notification_service_image.id
}

output "deliver_artifact_stage_id" {
  description = "OCID do stage que publica a imagem do notification-service no OCIR."
  value       = oci_devops_build_pipeline_stage.deliver_notification_service_image.id
}
