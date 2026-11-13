#
# nosql/outputs.tf
#

output "table_id" {
  description = "OCID da tabela principal pizzas em São Paulo."
  value       = oci_nosql_table.pizzas.id
}

output "replica_region" {
  description = "Região da réplica Global Active Table."
  value       = local.table_limits.replica_region
}

output "replica_id" {
  description = "Identificador da réplica criada em Vinhedo."
  value       = oci_nosql_table_replica.vcp.id
}

output "delivery_areas_table_id" {
  description = "OCID da tabela delivery_areas em São Paulo."
  value       = oci_nosql_table.delivery_areas.id
}

output "delivery_areas_replica_id" {
  description = "Identificador da réplica delivery_areas em Vinhedo."
  value       = oci_nosql_table_replica.delivery_areas_vcp.id
}

output "orders_table_id" {
  description = "OCID da tabela orders em São Paulo."
  value       = oci_nosql_table.orders.id
}

output "orders_replica_id" {
  description = "Identificador da réplica orders em Vinhedo."
  value       = oci_nosql_table_replica.orders_vcp.id
}
