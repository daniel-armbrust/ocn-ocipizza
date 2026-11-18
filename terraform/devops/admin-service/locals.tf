#
# devops/admin-service/locals.tf
#

locals {
  build_pipeline_name  = "admin-service"
  build_source_name    = "ocipizza-source"
  build_spec_file      = "services/admin-service/build_spec.yaml"
  output_artifact_name = "admin-service-image"
}
