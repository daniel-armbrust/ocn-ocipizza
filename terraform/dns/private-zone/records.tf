#
# dns/private-zone/records.tf
#

# Endpoints estáveis usados pela aplicação. O registro de escrita aponta para
# o primary de GRU nas duas regiões; o registro de leitura aponta para o MySQL
# regional, evitando leituras cross-region durante a operação normal.
resource "oci_dns_rrset" "mysql" {
  for_each = var.mysql_endpoints

  zone_name_or_id = oci_dns_zone.this.id
  domain          = local.mysql_domains[each.key]
  rtype           = "A"

  items {
    domain = local.mysql_domains[each.key]
    rdata  = each.value
    rtype  = "A"
    ttl    = 60
  }
}

# Nome estável do Redis usado nas duas regiões. Enquanto GRU for a região
# active, o CNAME aponta para o FQDN primário fornecido pelo OCI Cache de GRU.
resource "oci_dns_rrset" "redis" {
  zone_name_or_id = oci_dns_zone.this.id
  domain          = local.redis_domain
  rtype           = "CNAME"

  items {
    domain = local.redis_domain
    rdata  = local.redis_fqdn
    rtype  = "CNAME"
    ttl    = 30
  }
}

# Nomes estáveis das filas regionais. Os dois registros são publicados nas
# duas zonas privadas para permitir acesso explícito à fila de cada região.
resource "oci_dns_rrset" "queue" {
  for_each = local.queue_domains

  zone_name_or_id = oci_dns_zone.this.id
  domain          = each.value
  rtype           = "CNAME"

  items {
    domain = each.value
    rdata  = local.queue_fqdns[each.key]
    rtype  = "CNAME"
    ttl    = 60
  }
}
