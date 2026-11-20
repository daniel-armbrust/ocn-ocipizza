#
# devops/bootstrap/pizza-service/outputs.tf
#

output "build_stage_id" {
  description = "OCID do Managed Build stage de bootstrap do pizza-service."
  value       = oci_devops_build_pipeline_stage.bootstrap_pizza_service.id
}
