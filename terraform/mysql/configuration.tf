#
# mysql/configuration.tf
#

resource "oci_mysql_mysql_configuration" "this" {
  compartment_id = var.compartment_id
  shape_name     = "MySQL.2"
  display_name   = local.configuration_name
  description    = "Configuração do MySQL da OCI Pizza preparada para replicação cross-region."

  options {
    name  = "binlog_expire_logs_seconds"
    value = tostring(local.binlog_expire_logs_seconds)
  }
}
