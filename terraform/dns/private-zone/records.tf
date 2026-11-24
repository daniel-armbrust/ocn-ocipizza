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
