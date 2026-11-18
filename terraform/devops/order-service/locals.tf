#
# devops/order-service/locals.tf
#

locals {
  build_pipeline_name = "order-service"
  build_source_name   = "ocipizza-source"
  build_spec_file     = "services/order-service/build_spec.yaml"
}
