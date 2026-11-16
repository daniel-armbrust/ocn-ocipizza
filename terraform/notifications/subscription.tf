#
# notifications/subscription.tf
#

# A OCI envia um link ao endereço informado e só ativa a assinatura após a confirmação.
resource "oci_ons_subscription" "email" {
  compartment_id = var.compartment_id
  topic_id       = oci_ons_notification_topic.devops.id
  protocol       = "EMAIL"
  endpoint       = var.notification_email
}
