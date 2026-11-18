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

output "container_artifact_id" {
  description = "OCID do artefato de imagem do order-service no OCI DevOps."
  value       = oci_devops_deploy_artifact.order_service_image.id
}

output "deliver_artifact_stage_id" {
  description = "OCID do stage que publica a imagem do order-service no OCIR."
  value       = oci_devops_build_pipeline_stage.deliver_order_service_image.id
}
