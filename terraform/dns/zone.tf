#
# dns/zone.tf
#

# Zona DNS pública primária do domínio da aplicação.
resource "oci_dns_zone" "ocipizza" {
  compartment_id = var.compartment_id
  name           = local.domain_name
  scope          = "GLOBAL"
  zone_type      = "PRIMARY"
}
