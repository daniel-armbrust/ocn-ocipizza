#
# devops/chatbot-service/outputs.tf
#

output "build_pipeline_id" {
  description = "OCID da build pipeline do chatbot-service."
  value       = oci_devops_build_pipeline.chatbot_service.id
}

output "build_stage_id" {
  description = "OCID do Managed Build stage do chatbot-service."
  value       = oci_devops_build_pipeline_stage.build_chatbot_service.id
}

output "container_artifact_id" {
  description = "OCID do artefato de imagem do chatbot-service no OCI DevOps."
  value       = oci_devops_deploy_artifact.chatbot_service_image.id
}

output "deliver_artifact_stage_id" {
  description = "OCID do stage que publica a imagem do chatbot-service no OCIR."
  value       = oci_devops_build_pipeline_stage.deliver_chatbot_service_image.id
}
