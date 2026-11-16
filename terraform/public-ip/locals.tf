#
# public-ip/locals.tf
#

locals {
  # Nome administrativo do endereço reservado para o load balancer.
  display_name = "lb-${var.region_key}"
}
