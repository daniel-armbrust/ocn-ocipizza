#
# vcn-onpremises/route-table.tf
#

resource "oci_core_route_table" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "rt-onpremises-gru"

  dynamic "route_rules" {
    for_each = local.route_rules

    content {
      destination       = route_rules.value.destination
      destination_type  = route_rules.value.destination_type
      network_entity_id = local.gateway_ids[route_rules.value.target]
    }
  }
}
