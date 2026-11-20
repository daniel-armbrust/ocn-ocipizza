#
# devops/bootstrap/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da Build Pipeline bootstrap-ocipizza."
  value       = oci_devops_build_pipeline.bootstrap_ocipizza.id
}

output "pizza_service_stage_id" {
  description = "OCID do Managed Build stage de bootstrap do pizza-service."
  value       = module.pizza_service.build_stage_id
}
