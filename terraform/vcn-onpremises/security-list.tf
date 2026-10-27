#
# vcn-onpremises/security-list.tf
#

resource "oci_core_security_list" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "sl-onpremises-gru"

  # O ingresso permanece vazio de propósito: nenhuma conexão é iniciada
  # diretamente contra a rede on-premises simulada.
  dynamic "ingress_security_rules" {
    for_each = local.ingress_rules

    content {
      source      = ingress_security_rules.value.source
      source_type = ingress_security_rules.value.source_type
      protocol    = ingress_security_rules.value.protocol
      stateless   = ingress_security_rules.value.stateless
    }
  }

  dynamic "egress_security_rules" {
    for_each = local.egress_rules

    content {
      destination      = egress_security_rules.value.destination
      destination_type = egress_security_rules.value.destination_type
      protocol         = egress_security_rules.value.protocol
      stateless        = egress_security_rules.value.stateless
    }
  }
}
