#
# dns/private-zone/datasource.tf
#

# Obtém o resolver dedicado criado automaticamente para cada VCN regional.
data "oci_core_vcn_dns_resolver_association" "this" {
  for_each = var.vcn_ids

  vcn_id = each.value
}
