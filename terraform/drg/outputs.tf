#
# drg/outputs.tf
#

output "drg_id" {
  description = "OCID do DRG regional."
  value       = oci_core_drg.this.id
}

output "attachment_ids" {
  description = "Attachments das VCNs no DRG regional."
  value       = { for key, attachment in oci_core_drg_attachment.this : key => attachment.id }
}

output "route_table_ids" {
  description = "Tabelas de rotas regionais do DRG."
  value = {
    to_firewall    = oci_core_drg_route_table.to_firewall.id
    from_firewall  = oci_core_drg_route_table.from_firewall.id
    remote_peering = oci_core_drg_route_table.remote_peering.id
  }
}

output "firewall_vcn_route_table_id" {
  description = "OCID da VCN Route Table rt-to-firewall-ip."
  value       = oci_core_route_table.to_firewall_ip.id
}

output "from_firewall_import_distribution_id" {
  description = "OCID da Import Route Distribution da tabela from-firewall-drg-rt."
  value       = oci_core_drg_route_distribution.from_firewall.id
}
