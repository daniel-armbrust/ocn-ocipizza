#
# devops/bootstrap/mysql/locals.tf
#

locals {
  build_source_name = "ocipizza-source"
  build_spec_file   = "terraform/mysql/bootstrap/bootstrap_spec.yaml"
}
