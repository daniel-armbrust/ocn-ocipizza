#
# vcn-ci/datasource.tf
#

# Localiza os serviços OCI acessíveis pelo Service Gateway.
data "oci_core_services" "all" {
  filter {
    name   = "name"
    values = ["All .* Services In Oracle Services Network"]
    regex  = true
  }
}
