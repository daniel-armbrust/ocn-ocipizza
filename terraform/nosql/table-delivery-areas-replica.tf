#
# nosql/table-delivery-areas-replica.tf
#

# Réplica Global Active da tabela delivery_areas em Vinhedo.
resource "oci_nosql_table_replica" "delivery_areas_vcp" {
  compartment_id   = var.compartment_id
  table_name_or_id = oci_nosql_table.delivery_areas.id
  region           = local.table_limits.replica_region
  max_read_units   = local.table_limits.read_units
  max_write_units  = local.table_limits.write_units

  depends_on = [oci_nosql_table.delivery_areas]
}
