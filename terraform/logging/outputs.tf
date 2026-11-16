#
# logging/outputs.tf
#

output "log_group_id" {
  description = "OCID do grupo regional de logs da aplicação."
  value       = oci_logging_log_group.this.id
}

output "log_ids" {
  description = "OCIDs dos logs dos microsserviços por nome."
  value = {
    for name, log in oci_logging_log.service : name => log.id
  }
}
