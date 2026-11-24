#
# devops/bootstrap/user-service/outputs.tf
#

output "build_stage_id" {
  description = "OCID do Managed Build stage de bootstrap do user-service."
  value       = oci_devops_build_pipeline_stage.bootstrap_user_service.id
}
