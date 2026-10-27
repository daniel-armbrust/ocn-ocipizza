#
# dns/records.tf
#

# Publica o endereço reservado do Load Balancer em lb.ocipizza.com.br.
resource "oci_dns_rrset" "load_balancer" {
  zone_name_or_id = oci_dns_zone.ocipizza.id
  domain          = local.load_balancer_domain
  rtype           = "A"

  items {
    domain = local.load_balancer_domain
    rdata  = var.load_balancer_public_ip
    rtype  = "A"
    ttl    = 300
  }
}
