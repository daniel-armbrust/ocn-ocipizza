#
# email-delivery/sender.tf
#

# Registra o endereço que poderá aparecer no campo From dos e-mails.
resource "oci_email_sender" "no_reply" {
  compartment_id = var.compartment_id
  email_address  = local.sender_email

  # A criação depende do domínio e da chave DKIM desta região.
  depends_on = [oci_email_dkim.ocipizza]
}
