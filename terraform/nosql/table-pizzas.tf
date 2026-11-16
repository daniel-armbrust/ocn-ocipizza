#
# nosql/table-pizzas.tf
#

# Tabela principal criada na região de São Paulo (GRU).
resource "oci_nosql_table" "pizzas" {
  compartment_id = var.compartment_id
  name           = local.table_name
  ddl_statement  = local.ddl_statement
  table_limits {
    max_read_units     = local.table_limits.read_units
    max_write_units    = local.table_limits.write_units
    max_storage_in_gbs = local.table_limits.storage_gb
  }
}
