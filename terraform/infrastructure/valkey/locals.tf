#
# valkey/locals.tf
#

locals {
  # Nome regional do cluster utilizado pelos serviços da aplicação.
  display_name = "valkey-cache-${var.region_key}"

  # Configuração didática de alta disponibilidade do OCI Cache.
  node_count         = 3
  node_memory_in_gbs = 2
  cluster_mode       = "NONSHARDED"
  software_version   = "VALKEY_8_1"
}
