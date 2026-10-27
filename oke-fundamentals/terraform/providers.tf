#
# providers.tf
#

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 9.0"
    }
  }
}

provider "oci" {
  alias               = "gru"
  region              = local.regions.gru
  config_file_profile = var.oci_config_profile
}