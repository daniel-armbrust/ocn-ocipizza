#
# devops/bootstrap/pizza-service/providers.tf
#

terraform {
  required_providers {
    oci = {
      source = "oracle/oci"
    }
  }
}
