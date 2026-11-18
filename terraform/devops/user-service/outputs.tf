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
