#
# queue/queue.tf
#

# Fila regional de notificações do OCI Queue.
resource "oci_queue_queue" "notifications" {
  compartment_id = var.compartment_id
  display_name   = local.queue_name
}
