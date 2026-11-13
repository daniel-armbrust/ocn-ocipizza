#
# logging/logs.tf
#

# Logs customizados individuais para os microsserviços da aplicação.
resource "oci_logging_log" "service" {
  for_each = local.log_names

  display_name       = each.value
  log_group_id       = oci_logging_log_group.this.id
  log_type           = "CUSTOM"
  is_enabled         = true
  retention_duration = local.retention_duration
}
