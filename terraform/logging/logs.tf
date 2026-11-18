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

# Habilita os logs de build e deployment do projeto OCI DevOps em GRU. A
# decisão de criação usa um booleano conhecido durante o planejamento.
resource "oci_logging_log" "devops" {
  count = var.enable_devops_log ? 1 : 0

  display_name       = "log-ocipizza-devops"
  log_group_id       = oci_logging_log_group.this.id
  log_type           = "SERVICE"
  is_enabled         = true
  retention_duration = local.retention_duration

  configuration {
    compartment_id = var.compartment_id

    source {
      category    = "all"
      resource    = var.devops_project_id
      service     = "devops"
      source_type = "OCISERVICE"
    }
  }
}
