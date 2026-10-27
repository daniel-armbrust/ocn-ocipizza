#
# dns/outputs.tf
#

output "zone_id" {
  description = "OCID da zona DNS pública ocipizza.com.br."
  value       = oci_dns_zone.ocipizza.id
}

output "nameservers" {
  description = "Nameservers autoritativos atribuídos pela OCI à zona."
  value       = oci_dns_zone.ocipizza.nameservers[*].hostname
}

output "domain_name" {
  description = "Nome do domínio DNS público da aplicação."
  value       = oci_dns_zone.ocipizza.name
}
