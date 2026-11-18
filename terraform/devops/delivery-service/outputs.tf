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

output "container_artifact_id" {
  description = "OCID do artefato de imagem do delivery-service no OCI DevOps."
  value       = oci_devops_deploy_artifact.delivery_service_image.id
}

output "deliver_artifact_stage_id" {
  description = "OCID do stage que publica a imagem do delivery-service no OCIR."
  value       = oci_devops_build_pipeline_stage.deliver_delivery_service_image.id
}
