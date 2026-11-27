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

  redis_domain = "redis.${local.domain_name}"
  redis_fqdn   = "${trimsuffix(trimspace(var.redis_fqdn), ".")}."

  queue_domains = {
    gru = "queue-gru.${local.domain_name}"
    vcp = "queue-vcp.${local.domain_name}"
  }

  # messages_endpoint é uma URL HTTPS; registros CNAME aceitam somente o
  # hostname e devem usar o ponto final para representar um nome absoluto.
  queue_fqdns = {
    for key, endpoint in var.queue_messages_endpoints :
    key => "${trimsuffix(split("/", trimprefix(trimspace(endpoint), "https://"))[0], ".")}."
  }
}
