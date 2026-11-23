#
# dns/public-zone/providers.tf
#

terraform {
  required_providers {
    oci = {
      source = "oracle/oci"
    }
  }
}
