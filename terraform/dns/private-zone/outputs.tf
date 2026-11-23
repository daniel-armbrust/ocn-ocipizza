#
# dns/private-zone/outputs.tf
#

output "zone_id" {
  description = "OCID da zona DNS privada regional ocipizza.internal."
  value       = oci_dns_zone.this.id
}

output "view_id" {
  description = "OCID da Private View regional associada aos resolvers."
  value       = oci_dns_view.this.id
}

output "resolver_ids" {
  description = "Mapa dos OCIDs dos resolvers associados à Private View."
  value = {
    for key, resolver in data.oci_core_vcn_dns_resolver_association.this :
    key => resolver.dns_resolver_id
  }
}
