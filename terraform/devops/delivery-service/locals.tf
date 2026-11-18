#
# devops/delivery-service/locals.tf
#

locals {
  build_pipeline_name = "delivery-service"
  build_source_name   = "ocipizza-source"
  build_spec_file     = "services/delivery-service/build_spec.yaml"
}
