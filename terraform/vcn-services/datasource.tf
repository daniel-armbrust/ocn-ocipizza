#
# vcn-services/datasource.tf
#

# Localiza o conjunto de serviços OCI acessível pelo Service Gateway.
data "oci_core_services" "all" {
  filter {
    name   = "name"
    values = ["All .* Services In Oracle Services Network"]
    regex  = true
  }
}
