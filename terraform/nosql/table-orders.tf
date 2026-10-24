#
# nosql/table-orders.tf
#

# Tabela principal dos pedidos, criada na região de São Paulo.
resource "oci_nosql_table" "orders" {
  compartment_id = var.compartment_id
  name           = local.orders_table_name
  ddl_statement  = local.orders_ddl_statement
  table_limits {
    max_read_units     = local.table_limits.read_units
    max_write_units    = local.table_limits.write_units
    max_storage_in_gbs = local.table_limits.storage_gb
  }
}
