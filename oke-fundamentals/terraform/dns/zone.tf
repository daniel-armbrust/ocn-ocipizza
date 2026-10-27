#
# dns/zone.tf
#

# Cria a zona pública autoritativa. Após o apply, os nameservers publicados
# nos outputs devem ser configurados no registrador do domínio.
resource "oci_dns_zone" "ocipizza" {
  compartment_id = var.compartment_id
  name           = local.domain_name
  scope          = "GLOBAL"
  zone_type      = "PRIMARY"
}
