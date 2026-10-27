#
# dns/locals.tf
#

locals {
  # Domínio público utilizado pela aplicação OCI Pizza.
  domain_name = "ocipizza.com.br"

  # Nome completo publicado para o Load Balancer do OKE.
  load_balancer_domain = "lb.${local.domain_name}"
}
