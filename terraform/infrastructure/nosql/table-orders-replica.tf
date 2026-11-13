#
# nosql/table-orders-replica.tf
#

# Réplica Global Active da tabela orders em Vinhedo.
resource "oci_nosql_table_replica" "orders_vcp" {
  compartment_id   = var.compartment_id
  table_name_or_id = oci_nosql_table.orders.id
  region           = local.table_limits.replica_region
  max_read_units   = local.table_limits.read_units
  max_write_units  = local.table_limits.write_units

  depends_on = [oci_nosql_table.orders]
}
