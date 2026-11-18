#
# devops/user-service/locals.tf
#

locals {
  build_pipeline_name  = "user-service"
  build_source_name    = "ocipizza-source"
  build_spec_file      = "services/user-service/build_spec.yaml"
  output_artifact_name = "user-service-image"
}
