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
