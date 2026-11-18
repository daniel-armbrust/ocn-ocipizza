#
# devops/chatbot-service/locals.tf
#

locals {
  build_pipeline_name  = "chatbot-service"
  build_source_name    = "ocipizza-source"
  build_spec_file      = "services/chatbot-service/build_spec.yaml"
  output_artifact_name = "chatbot-service-image"
}
