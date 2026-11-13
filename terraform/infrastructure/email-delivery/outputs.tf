#
# email-delivery/outputs.tf
#

output "email_domain_id" {
  description = "OCID do domínio de e-mail do OCI Pizza."
  value       = oci_email_email_domain.ocipizza.id
}

output "sender_id" {
  description = "OCID do remetente aprovado no Email Delivery."
  value       = oci_email_sender.no_reply.id
}

output "sender_email" {
  description = "Endereço de e-mail aprovado para envio."
  value       = oci_email_sender.no_reply.email_address
}

output "dkim_record" {
  description = "Registro CNAME que deve ser publicado na zona DNS pública."
  value = {
    domain = oci_email_dkim.ocipizza.dns_subdomain_name
    value  = oci_email_dkim.ocipizza.cname_record_value
  }
}
