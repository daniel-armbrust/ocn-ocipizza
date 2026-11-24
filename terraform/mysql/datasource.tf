#
# mysql/datasource.tf
#

data "oci_identity_availability_domains" "this" {
  compartment_id = var.compartment_id
}
