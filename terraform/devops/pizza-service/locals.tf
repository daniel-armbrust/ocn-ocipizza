#
# devops/pizza-service/locals.tf
#

locals {
  build_pipeline_name = "pizza-service"
  build_source_name   = "ocipizza-source"
  build_spec_file     = "services/pizza-service/build_spec.yaml"
}
