#
# vcn-db/security-list.tf
#

resource "oci_core_security_list" "this" {
  for_each       = local.config.security_lists
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = each.value.name

  dynamic "ingress_security_rules" {
    for_each = each.value.ingress

    content {
      source      = ingress_security_rules.value.source
      source_type = ingress_security_rules.value.source_type
      protocol    = ingress_security_rules.value.protocol
      stateless   = ingress_security_rules.value.stateless
    }
  }

  dynamic "egress_security_rules" {
    for_each = each.value.egress

    content {
      destination      = egress_security_rules.value.destination
      destination_type = egress_security_rules.value.destination_type
      protocol         = egress_security_rules.value.protocol
      stateless        = egress_security_rules.value.stateless
    }
  }
}
