#
# devops/bootstrap/pizza-service/locals.tf
#

locals {
  build_source_name = "ocipizza-source"
  build_spec_file   = "services/pizza-service/bootstrap_spec.yaml"
}
