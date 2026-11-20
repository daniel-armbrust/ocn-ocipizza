#
# oci-cache/locals.tf
#

locals {
  # Nome regional do cluster utilizado pelos serviços da aplicação.
  display_name = "redis-cache-${var.region_key}"

  # Nome do Configuration Set regional exigido pela replicação cross-region.
  config_set_display_name = "redis-cache-config-${var.region_key}"

  # A replicação cross-region exige clusters NONSHARDED com, no mínimo,
  # 8 GB de memória por nó e a mesma versão do engine nas duas regiões.
  # Um nó por região reduz o custo do ambiente didático. Essa configuração
  # mantém a replicação cross-region, mas não oferece redundância regional.
  node_count         = 1
  node_memory_in_gbs = 8
  cluster_mode       = "NONSHARDED"
  software_version   = "REDIS_7_0"
}
