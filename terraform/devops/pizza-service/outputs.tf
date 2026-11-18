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

output "container_artifact_id" {
  description = "OCID do artefato de imagem do pizza-service no OCI DevOps."
  value       = oci_devops_deploy_artifact.pizza_service_image.id
}

output "deliver_artifact_stage_id" {
  description = "OCID do stage que publica a imagem do pizza-service no OCIR."
  value       = oci_devops_build_pipeline_stage.deliver_pizza_service_image.id
}
