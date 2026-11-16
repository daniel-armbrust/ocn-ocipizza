#
# email-delivery/dkim.tf
#

# Gera a chave DKIM que assinará os remetentes do domínio nesta região.
resource "oci_email_dkim" "ocipizza" {
  email_domain_id = oci_email_email_domain.ocipizza.id
  name            = local.dkim_selector
}
