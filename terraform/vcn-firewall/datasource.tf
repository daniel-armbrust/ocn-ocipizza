#
# vcn-firewall/datasource.tf
#

# Localiza o conjunto de serviços que pode ser acessado pelo SGW.
data "oci_core_services" "all" {
  filter {
    name   = "name"
    values = ["All .* Services In Oracle Services Network"]
    regex  = true
  }
}
