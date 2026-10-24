#
# logging/log-group.tf
#

# Grupo regional que reúne todos os logs dos microsserviços.
resource "oci_logging_log_group" "this" {
  compartment_id = var.compartment_id
  display_name   = local.log_group_name
}
