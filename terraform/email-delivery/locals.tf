#
# email-delivery/locals.tf
#

locals {
  # Domínio utilizado para autenticar os e-mails enviados pela aplicação.
  email_domain = "ocipizza.com.br"

  # Remetente aprovado utilizado pelo notification-service.
  sender_email = "no-reply@ocipizza.com.br"

  # O seletor precisa ser diferente em cada região.
  dkim_selector = "ocipizza-${var.region_key}"
}
