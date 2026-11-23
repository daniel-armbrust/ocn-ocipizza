#
# dns/private-zone/zone.tf
#

# Zona DNS privada e independente da região correspondente.
resource "oci_dns_zone" "this" {
  compartment_id = var.compartment_id
  name           = local.domain_name
  scope          = "PRIVATE"
  view_id        = oci_dns_view.this.id
  zone_type      = "PRIMARY"
}
