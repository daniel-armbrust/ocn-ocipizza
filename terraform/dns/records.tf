#
# dns/records.tf
#

# Registros A para os endereços reservados dos load balancers regionais.
resource "oci_dns_rrset" "load_balancer" {
  for_each = var.load_balancer_public_ips

  zone_name_or_id = oci_dns_zone.ocipizza.id
  domain          = local.load_balancer_domains[each.key]
  rtype           = "A"

  items {
    domain = local.load_balancer_domains[each.key]
    rdata  = each.value
    rtype  = "A"
    ttl    = 300
  }
}

# Autoriza os servidores do OCI Email Delivery para o domínio da aplicação.
resource "oci_dns_rrset" "email_spf" {
  zone_name_or_id = oci_dns_zone.ocipizza.id
  domain          = local.domain_name
  rtype           = "TXT"

  items {
    domain = local.domain_name
    rdata  = local.email_spf_record
    rtype  = "TXT"
    ttl    = 300
  }
}

# Publica os CNAMEs DKIM fornecidos pelo OCI Email Delivery.
resource "oci_dns_rrset" "email_dkim" {
  for_each = var.email_dkim_records

  zone_name_or_id = oci_dns_zone.ocipizza.id
  domain          = each.value.domain
  rtype           = "CNAME"

  items {
    domain = each.value.domain
    rdata  = each.value.value
    rtype  = "CNAME"
    ttl    = 300
  }
}
