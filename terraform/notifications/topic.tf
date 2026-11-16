#
# notifications/topic.tf
#

# Topic regional usado pelo projeto OCI DevOps para publicar seus eventos.
resource "oci_ons_notification_topic" "devops" {
  compartment_id = var.compartment_id
  name           = local.topic_name
  description    = "Notificações do projeto OCI DevOps do OCI Pizza."
}
