#
# dns/locals.tf
#

locals {
  # Domínio público utilizado pela aplicação OCI Pizza.
  domain_name = "ocipizza.com.br"

  # Nomes completos usados pelos load balancers regionais no DNS público.
  load_balancer_domains = {
    gru = "lb-gru.${local.domain_name}"
    vcp = "lb-vcp.${local.domain_name}"
  }

  # SPF das regiões comerciais das Américas.
  email_spf_record = "\"v=spf1 include:rp.oracleemaildelivery.com ~all\""
}
