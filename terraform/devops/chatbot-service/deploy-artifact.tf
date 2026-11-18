#
# devops/chatbot-service/deploy-artifact.tf
#

# Artefato de container que representa a imagem persistida no OCIR.
resource "oci_devops_deploy_artifact" "chatbot_service_image" {
  project_id                 = var.project_id
  display_name               = local.output_artifact_name
  description                = "Imagem de container do chatbot-service publicada pelo Managed Build."
  deploy_artifact_type       = "DOCKER_IMAGE"
  argument_substitution_mode = "SUBSTITUTE_PLACEHOLDERS"

  deploy_artifact_source {
    deploy_artifact_source_type = "OCIR"
    image_uri                   = "${var.container_repository_url}:$${BUILDRUN_HASH}"
  }
}
