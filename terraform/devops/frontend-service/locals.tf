#
# devops/frontend-service/locals.tf
#

locals {
  build_pipeline_name = "frontend-service"
  build_source_name   = "ocipizza-source"
  build_spec_file     = "services/frontend-service/build_spec.yaml"
}
