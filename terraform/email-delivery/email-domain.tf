#
# email-delivery/email-domain.tf
#

# Registra o domínio de envio no OCI Email Delivery.
resource "oci_email_email_domain" "ocipizza" {
  compartment_id = var.compartment_id
  name           = local.email_domain
}
