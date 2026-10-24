#
# vcn-firewall/security-list.tf
#

# Cria uma Security List independente para cada sub-rede.
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

      dynamic "tcp_options" {
        for_each = try(ingress_security_rules.value.tcp_options, null) == null ? [] : [
          ingress_security_rules.value.tcp_options
        ]
        content {
          min = tcp_options.value.min
          max = tcp_options.value.max
        }
      }
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
