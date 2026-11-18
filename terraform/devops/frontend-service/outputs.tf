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
