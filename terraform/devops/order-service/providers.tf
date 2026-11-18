#
# devops/order-service/providers.tf
#

terraform {
  required_providers {
    oci = {
      source = "oracle/oci"
    }
  }
}
