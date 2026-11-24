#
# dns/private-zone/locals.tf
#

locals {
  domain_name       = "ocipizza.internal"
  private_view_name = "ocipizza-internal-${var.region_key}"

  mysql_domains = {
    write = "mysql-write.${local.domain_name}"
    read  = "mysql-read.${local.domain_name}"
  }
}
