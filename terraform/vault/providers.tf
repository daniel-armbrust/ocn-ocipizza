#
# vault/providers.tf
#

terraform {
  required_providers {
    external = {
      source = "hashicorp/external"
    }

    oci = {
      source = "oracle/oci"
    }
  }
}
