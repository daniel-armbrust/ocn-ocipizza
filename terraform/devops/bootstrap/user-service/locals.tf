#
# devops/bootstrap/user-service/locals.tf
#

locals {
  build_source_name = "ocipizza-source"
  build_spec_file   = "services/user-service/bootstrap_spec.yaml"
}
