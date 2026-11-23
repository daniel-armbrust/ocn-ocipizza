#
# dns/private-zone/locals.tf
#

locals {
  domain_name       = "ocipizza.internal"
  private_view_name = "ocipizza-internal-${var.region_key}"
}
