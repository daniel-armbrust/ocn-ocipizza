#
# nosql/table-delivery-areas.tf
#

# Tabela principal das áreas de entrega, criada na região de São Paulo.
resource "oci_nosql_table" "delivery_areas" {
  compartment_id = var.compartment_id
  name           = local.delivery_areas_table_name
  ddl_statement  = local.delivery_areas_ddl_statement
  table_limits {
    max_read_units     = local.table_limits.read_units
    max_write_units    = local.table_limits.write_units
    max_storage_in_gbs = local.table_limits.storage_gb
  }
}
