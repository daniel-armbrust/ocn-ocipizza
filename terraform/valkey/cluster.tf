#
# valkey/cluster.tf
#

# Cluster privado OCI Cache com engine Valkey.
resource "oci_redis_redis_cluster" "this" {
  compartment_id     = var.compartment_id
  display_name       = local.display_name
  node_count         = local.node_count
  node_memory_in_gbs = local.node_memory_in_gbs
  software_version   = local.software_version
  subnet_id          = var.subnet_id
  cluster_mode       = local.cluster_mode
}
