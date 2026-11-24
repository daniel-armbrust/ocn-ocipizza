#
# mysql/outputs.tf
#

output "db_system_id" {
  description = "OCID do MySQL DB System regional."
  value       = oci_mysql_mysql_db_system.this.id
}

output "endpoint" {
  description = "Endpoint privado principal do MySQL DB System regional."
  value = {
    hostname = oci_mysql_mysql_db_system.this.endpoints[0].hostname
    ip       = oci_mysql_mysql_db_system.this.endpoints[0].ip_address
    port     = oci_mysql_mysql_db_system.this.endpoints[0].port
  }
}
