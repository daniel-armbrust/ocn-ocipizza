#
# notifications/outputs.tf
#

output "topic_id" {
  description = "OCID do Topic usado pelas notificações do OCI DevOps."
  value       = oci_ons_notification_topic.devops.id
}

output "subscription_id" {
  description = "OCID da assinatura de e-mail do Topic."
  value       = oci_ons_subscription.email.id
}
