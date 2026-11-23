#
# dns/private-zone/resolver.tf
#

# Anexa a Private View ao resolver de cada VCN. As sub-redes dessas VCNs já
# usam VcnLocalPlusInternet nos DHCP Options e passam a resolver a zona.
resource "oci_dns_resolver" "this" {
  for_each = data.oci_core_vcn_dns_resolver_association.this

  resolver_id = each.value.dns_resolver_id
  scope       = "PRIVATE"

  attached_views {
    view_id = oci_dns_view.this.id
  }
}
