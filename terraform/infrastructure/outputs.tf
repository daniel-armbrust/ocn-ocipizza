#
# outputs.tf
#

output "vcn_firewall_gru_id" {
  description = "OCID da VCN-FIREWALL em São Paulo."
  value       = module.vcn_firewall_gru.vcn_id
}

output "vcn_firewall_vcp_id" {
  description = "OCID da VCN-FIREWALL em Vinhedo."
  value       = module.vcn_firewall_vcp.vcn_id
}

output "vcn_firewall_gru_subnet_ids" {
  description = "Sub-redes da VCN-FIREWALL em São Paulo."
  value       = module.vcn_firewall_gru.subnet_ids
}

output "vcn_firewall_vcp_subnet_ids" {
  description = "Sub-redes da VCN-FIREWALL em Vinhedo."
  value       = module.vcn_firewall_vcp.subnet_ids
}

output "vcn_oke_gru_id" {
  description = "OCID da VCN-OKE em São Paulo."
  value       = module.vcn_oke_gru.vcn_id
}

output "vcn_oke_vcp_id" {
  description = "OCID da VCN-OKE em Vinhedo."
  value       = module.vcn_oke_vcp.vcn_id
}

output "vcn_oke_gru_subnet_ids" {
  description = "Sub-redes da VCN-OKE em São Paulo."
  value       = module.vcn_oke_gru.subnet_ids
}

output "vcn_oke_vcp_subnet_ids" {
  description = "Sub-redes da VCN-OKE em Vinhedo."
  value       = module.vcn_oke_vcp.subnet_ids
}

output "oke_gru_id" {
  description = "OCID do cluster OKE em São Paulo."
  value       = module.oke_gru.cluster_id
}

output "oke_vcp_id" {
  description = "OCID do cluster OKE em Vinhedo."
  value       = module.oke_vcp.cluster_id
}

output "oke_gru_node_pool_id" {
  description = "OCID do node pool OKE em São Paulo."
  value       = module.oke_gru.node_pool_id
}

output "oke_vcp_node_pool_id" {
  description = "OCID do node pool OKE em Vinhedo."
  value       = module.oke_vcp.node_pool_id
}

output "vcn_db_gru_id" {
  description = "OCID da VCN-DB em São Paulo."
  value       = module.vcn_db_gru.vcn_id
}

output "vcn_db_vcp_id" {
  description = "OCID da VCN-DB em Vinhedo."
  value       = module.vcn_db_vcp.vcn_id
}

output "vcn_db_gru_subnet_ids" {
  description = "Sub-rede da VCN-DB em São Paulo."
  value       = module.vcn_db_gru.subnet_ids
}

output "vcn_db_vcp_subnet_ids" {
  description = "Sub-rede da VCN-DB em Vinhedo."
  value       = module.vcn_db_vcp.subnet_ids
}

output "vcn_services_gru_id" {
  description = "OCID da VCN-SERVICES em São Paulo."
  value       = module.vcn_services_gru.vcn_id
}

output "vcn_services_vcp_id" {
  description = "OCID da VCN-SERVICES em Vinhedo."
  value       = module.vcn_services_vcp.vcn_id
}

output "vcn_services_gru_subnet_ids" {
  description = "Sub-rede da VCN-SERVICES em São Paulo."
  value       = module.vcn_services_gru.subnet_ids
}

output "vcn_services_vcp_subnet_ids" {
  description = "Sub-rede da VCN-SERVICES em Vinhedo."
  value       = module.vcn_services_vcp.subnet_ids
}

output "vcn_onpremises_gru_id" {
  description = "OCID da VCN on-premises simulada em GRU."
  value       = module.vcn_onpremises_gru.vcn_id
}

output "vcn_onpremises_gru_subnet_id" {
  description = "OCID da sub-rede pública on-premises simulada em GRU."
  value       = module.vcn_onpremises_gru.subnet_id
}

output "vcn_ci_gru_id" {
  description = "OCID da VCN-CI em São Paulo."
  value       = module.vcn_ci_gru.vcn_id
}

output "vcn_ci_vcp_id" {
  description = "OCID da VCN-CI em Vinhedo."
  value       = module.vcn_ci_vcp.vcn_id
}

output "vcn_ci_gru_subnet_ids" {
  description = "Sub-redes da VCN-CI em São Paulo."
  value       = module.vcn_ci_gru.subnet_ids
}

output "vcn_ci_vcp_subnet_ids" {
  description = "Sub-redes da VCN-CI em Vinhedo."
  value       = module.vcn_ci_vcp.subnet_ids
}

output "valkey_gru_id" {
  description = "OCID do cluster Valkey em São Paulo."
  value       = module.valkey_gru.cluster_id
}

output "valkey_vcp_id" {
  description = "OCID do cluster Valkey em Vinhedo."
  value       = module.valkey_vcp.cluster_id
}

output "logging_gru_log_group_id" {
  description = "OCID do grupo de logs em São Paulo."
  value       = module.logging_gru.log_group_id
}

output "logging_vcp_log_group_id" {
  description = "OCID do grupo de logs em Vinhedo."
  value       = module.logging_vcp.log_group_id
}

output "drg_gru_id" {
  description = "OCID do DRG de São Paulo."
  value       = module.drg_gru.drg_id
}

output "drg_vcp_id" {
  description = "OCID do DRG de Vinhedo."
  value       = module.drg_vcp.drg_id
}

output "remote_peering_gru_id" {
  description = "OCID do RPC de São Paulo."
  value       = oci_core_remote_peering_connection.gru.id
}

output "remote_peering_vcp_id" {
  description = "OCID do RPC de Vinhedo."
  value       = oci_core_remote_peering_connection.vcp.id
}

output "compute_firewall_gru_id" {
  description = "OCID do Compute Firewall em São Paulo."
  value       = module.compute_firewall_gru.instance_id
}

output "compute_firewall_vcp_id" {
  description = "OCID do Compute Firewall em Vinhedo."
  value       = module.compute_firewall_vcp.instance_id
}

output "compute_firewall_gru_trust_vnic_id" {
  description = "OCID legado da VNIC TRUST em São Paulo."
  value       = module.compute_firewall_gru.trust_vnic_id
}

output "compute_firewall_vcp_trust_vnic_id" {
  description = "OCID legado da VNIC TRUST em Vinhedo."
  value       = module.compute_firewall_vcp.trust_vnic_id
}

output "notifications_queue_gru_id" {
  description = "OCID da fila em São Paulo."
  value       = module.queue_gru.queue_id
}

output "notifications_queue_vcp_id" {
  description = "OCID da fila em Vinhedo."
  value       = module.queue_vcp.queue_id
}
