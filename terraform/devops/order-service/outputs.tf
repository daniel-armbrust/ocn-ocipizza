#
# devops/order-service/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da build pipeline do order-service."
  value       = oci_devops_build_pipeline.order_service.id
}

output "build_stage_id" {
  description = "OCID do Managed Build stage do order-service."
  value       = oci_devops_build_pipeline_stage.build_order_service.id
}
