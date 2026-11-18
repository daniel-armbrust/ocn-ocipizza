#
# devops/pizza-service/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da build pipeline do pizza-service."
  value       = oci_devops_build_pipeline.pizza_service.id
}

output "build_stage_id" {
  description = "OCID do Managed Build stage do pizza-service."
  value       = oci_devops_build_pipeline_stage.build_pizza_service.id
}
