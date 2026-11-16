#
# queue/outputs.tf
#

output "queue_id" {
  description = "OCID da fila regional de notificações."
  value       = oci_queue_queue.notifications.id
}

output "messages_endpoint" {
  description = "Endpoint regional usado para publicar e consumir mensagens."
  value       = oci_queue_queue.notifications.messages_endpoint
}

output "queue_name" {
  description = "Nome da fila regional de notificações."
  value       = oci_queue_queue.notifications.display_name
}
