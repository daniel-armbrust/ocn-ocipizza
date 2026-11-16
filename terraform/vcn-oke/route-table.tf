#
# vcn-oke/route-table.tf
#

resource "oci_core_route_table" "this" {
  for_each       = local.config.route_tables
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = each.value.name

  dynamic "route_rules" {
    for_each = [
      for rule in each.value.rules : rule
      if rule.target != "drg" || var.drg_id != null
    ]

    content {
      # O destino SERVICE_CIDR_BLOCK usa o CIDR publicado pelo Oracle
      # Services Network; os demais destinos permanecem literais.
      destination       = route_rules.value.target == "service" ? data.oci_core_services.all.services[0].cidr_block : route_rules.value.destination
      destination_type  = route_rules.value.destination_type
      network_entity_id = route_rules.value.target == "drg" ? var.drg_id : local.gateway_ids[route_rules.value.target]
    }
  }
}
