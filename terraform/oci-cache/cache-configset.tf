#
# oci-cache/cache-configset.tf
#

# Configuration Set regional usado pelos clusters que participam da
# replicação cross-region. Os valores devem permanecer equivalentes em GRU e
# VCP para permitir a associação entre o primary e o secondary.
resource "oci_redis_oci_cache_config_set" "this" {
  compartment_id   = var.compartment_id
  display_name     = local.config_set_display_name
  description      = "Configuração do OCI Cache para replicação cross-region ${upper(var.region_key)}."
  software_version = local.software_version

  configuration_details {
    # A OCI exige pelo menos 35% de memória reservada quando há replicação
    # cross-region. Essa reserva fornece espaço operacional ao engine.
    items {
      config_key   = "reserved-memory-percentage"
      config_value = "35"
    }

    # Uma política de eviction é obrigatória, pois noeviction não é aceita em
    # clusters que participam da replicação cross-region.
    items {
      config_key   = "maxmemory-policy"
      config_value = "allkeys-lru"
    }
  }

  # A OCI não permite remover ou substituir configurações customizadas
  # enquanto o Configuration Set estiver associado a um cluster ativo. O
  # provider pode detectar diferenças de normalização e tentar atualizar os
  # itens em applies posteriores, operação que falha no serviço. Os valores
  # continuam sendo aplicados na criação inicial; mudanças futuras exigem um
  # procedimento controlado de desassociação ou recriação dos clusters.
  lifecycle {
    ignore_changes = [
      configuration_details,
    ]
  }
}
