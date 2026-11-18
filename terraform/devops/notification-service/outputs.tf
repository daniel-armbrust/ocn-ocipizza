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
