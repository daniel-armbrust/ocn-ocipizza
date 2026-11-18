#
# devops/notification-service/locals.tf
#

locals {
  build_pipeline_name  = "notification-service"
  build_source_name    = "ocipizza-source"
  build_spec_file      = "services/notification-service/build_spec.yaml"
  output_artifact_name = "notification-service-image"
}
