#
# nosql/table-pizzas-replica.tf
#

# Replica Global Active Table criada em Vinhedo (VCP). A operação é enviada
# pelo provider da região principal e o atributo region identifica a região
# remota que receberá a cópia com leitura e escrita próprias.
resource "oci_nosql_table_replica" "vcp" {
  compartment_id   = var.compartment_id
  table_name_or_id = oci_nosql_table.pizzas.id
  region           = local.table_limits.replica_region
  max_read_units   = local.table_limits.read_units
  max_write_units  = local.table_limits.write_units

  depends_on = [oci_nosql_table.pizzas]
}
