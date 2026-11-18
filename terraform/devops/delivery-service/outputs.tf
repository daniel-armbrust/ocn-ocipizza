#
# devops/delivery-service/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da build pipeline do delivery-service."
  value       = oci_devops_build_pipeline.delivery_service.id
}

output "build_stage_id" {
  description = "OCID do Managed Build stage do delivery-service."
  value       = oci_devops_build_pipeline_stage.build_delivery_service.id
}
