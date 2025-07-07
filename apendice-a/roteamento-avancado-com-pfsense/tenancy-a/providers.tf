#
# providers.tf
#

provider "oci" {
  alias = "home_region"

  region = "sa-saopaulo-1"
  fingerprint = var.api_fingerprint
  private_key_path = var.api_private_key_path  
  tenancy_ocid = var.tenancy_id
  user_ocid = var.user_id
}

provider "oci" {
  alias = "gru"

  region = "sa-saopaulo-1"
  fingerprint = var.api_fingerprint
  private_key_path = var.api_private_key_path  
  tenancy_ocid = var.tenancy_id
  user_ocid = var.user_id
}

provider "oci" {
  alias = "vcp"
  
  region = "sa-vinhedo-1"
  fingerprint = var.api_fingerprint
  private_key_path = var.api_private_key_path  
  tenancy_ocid = var.tenancy_id
  user_ocid = var.user_id
}