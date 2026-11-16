#
# compute-firewall/outputs.tf
#

output "instance_id" {
  description = "OCID da instância de firewall."
  value       = oci_core_instance.this.id
}

output "primary_vnic_id" {
  description = "OCID da única VNIC do firewall."
  value       = local.primary_vnic_id
}

output "trust_vnic_id" {
  description = "Alias legado; não existe VNIC TRUST na nova topologia."
  value       = null
}

output "trust_private_ip" {
  description = "Endereço IPv4 privado da única VNIC do firewall."
  value       = data.oci_core_private_ips.primary.private_ips[0].ip_address
}

output "trust_private_ip_id" {
  description = "Alias legado para o OCID do IP privado da VNIC do firewall."
  value       = data.oci_core_private_ips.primary.private_ips[0].id
}

output "untrust_vnic_id" {
  description = "Alias legado; não existe VNIC UNTRUST na nova topologia."
  value       = null
}
