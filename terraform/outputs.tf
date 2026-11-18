#
# outputs.tf
#

output "iam_instances_dynamic_group_id" {
  description = "OCID do dynamic group dos workloads do OCI Pizza."
  value       = oci_identity_dynamic_group.ocipizza_instances.id
}

output "iam_devops_dynamic_group_id" {
  description = "OCID do dynamic group dos resource principals do OCI DevOps."
  value       = oci_identity_dynamic_group.ocipizza_devops.id
}

output "iam_instance_principals_policy_id" {
  description = "OCID da policy dos Instance Principals do OCI Pizza."
  value       = oci_identity_policy.ocipizza_instance_principals.id
}

output "iam_devops_policy_id" {
  description = "OCID da policy das pipelines do OCI DevOps."
  value       = oci_identity_policy.ocipizza_devops.id
}

output "iam_service_principals_policy_id" {
  description = "OCID da policy dos serviços gerenciados."
  value       = oci_identity_policy.ocipizza_service_principals.id
}

output "notifications_topic_id" {
  description = "OCID do Topic de notificações usado pelo OCI DevOps em São Paulo."
  value       = module.notifications_gru.topic_id
}

output "notifications_email_subscription_id" {
  description = "OCID da assinatura de e-mail do Topic do OCI DevOps."
  value       = module.notifications_gru.subscription_id
}

output "vault_id" {
  description = "OCID do Vault persistente do OCI Pizza em São Paulo."
  value       = module.vault_gru.vault_id
}

output "vault_key_id" {
  description = "OCID da chave que criptografa os Secrets do OCI Pizza."
  value       = module.vault_gru.key_id
}

output "github_pat_secret_id" {
  description = "OCID do Secret que contém o PAT do GitHub."
  value       = module.vault_gru.github_pat_secret_id
}

output "ocir_pizza_service_repository_id" {
  description = "OCID do repositório de imagens do pizza-service no OCIR de São Paulo."
  value       = module.ocir_gru.pizza_service_repository_id
}

output "ocir_pizza_service_repository_name" {
  description = "Nome do repositório de imagens do pizza-service no OCIR."
  value       = module.ocir_gru.pizza_service_repository_name
}

output "ocir_pizza_service_repository_namespace" {
  description = "Namespace da tenancy usado pelo repositório do pizza-service no OCIR."
  value       = module.ocir_gru.pizza_service_repository_namespace
}

output "ocir_pizza_service_repository_url" {
  description = "URL completa do repositório do pizza-service no OCIR, sem tag."
  value       = module.ocir_gru.pizza_service_repository_url
}

output "ocir_user_service_repository_id" {
  description = "OCID do repositório de imagens do user-service no OCIR de São Paulo."
  value       = module.ocir_gru.user_service_repository_id
}

output "ocir_user_service_repository_name" {
  description = "Nome do repositório de imagens do user-service no OCIR."
  value       = module.ocir_gru.user_service_repository_name
}

output "ocir_user_service_repository_url" {
  description = "URL completa do repositório do user-service no OCIR, sem tag."
  value       = module.ocir_gru.user_service_repository_url
}

output "ocir_admin_service_repository_id" {
  description = "OCID do repositório de imagens do admin-service no OCIR de São Paulo."
  value       = module.ocir_gru.admin_service_repository_id
}

output "ocir_admin_service_repository_name" {
  description = "Nome do repositório de imagens do admin-service no OCIR."
  value       = module.ocir_gru.admin_service_repository_name
}

output "ocir_admin_service_repository_url" {
  description = "URL completa do repositório do admin-service no OCIR, sem tag."
  value       = module.ocir_gru.admin_service_repository_url
}

output "ocir_chatbot_service_repository_id" {
  description = "OCID do repositório de imagens do chatbot-service no OCIR de São Paulo."
  value       = module.ocir_gru.chatbot_service_repository_id
}

output "ocir_chatbot_service_repository_name" {
  description = "Nome do repositório de imagens do chatbot-service no OCIR."
  value       = module.ocir_gru.chatbot_service_repository_name
}

output "ocir_chatbot_service_repository_url" {
  description = "URL completa do repositório do chatbot-service no OCIR, sem tag."
  value       = module.ocir_gru.chatbot_service_repository_url
}

output "ocir_delivery_service_repository_id" {
  description = "OCID do repositório de imagens do delivery-service no OCIR de São Paulo."
  value       = module.ocir_gru.delivery_service_repository_id
}

output "ocir_delivery_service_repository_name" {
  description = "Nome do repositório de imagens do delivery-service no OCIR."
  value       = module.ocir_gru.delivery_service_repository_name
}

output "ocir_delivery_service_repository_url" {
  description = "URL completa do repositório do delivery-service no OCIR, sem tag."
  value       = module.ocir_gru.delivery_service_repository_url
}

output "ocir_frontend_service_repository_id" {
  description = "OCID do repositório de imagens do frontend-service no OCIR de São Paulo."
  value       = module.ocir_gru.frontend_service_repository_id
}

output "ocir_frontend_service_repository_name" {
  description = "Nome do repositório de imagens do frontend-service no OCIR."
  value       = module.ocir_gru.frontend_service_repository_name
}

output "ocir_frontend_service_repository_url" {
  description = "URL completa do repositório do frontend-service no OCIR, sem tag."
  value       = module.ocir_gru.frontend_service_repository_url
}

output "ocir_notification_service_repository_id" {
  description = "OCID do repositório de imagens do notification-service no OCIR de São Paulo."
  value       = module.ocir_gru.notification_service_repository_id
}

output "ocir_notification_service_repository_name" {
  description = "Nome do repositório de imagens do notification-service no OCIR."
  value       = module.ocir_gru.notification_service_repository_name
}

output "ocir_notification_service_repository_url" {
  description = "URL completa do repositório do notification-service no OCIR, sem tag."
  value       = module.ocir_gru.notification_service_repository_url
}

output "ocir_order_service_repository_id" {
  description = "OCID do repositório de imagens do order-service no OCIR de São Paulo."
  value       = module.ocir_gru.order_service_repository_id
}

output "ocir_order_service_repository_name" {
  description = "Nome do repositório de imagens do order-service no OCIR."
  value       = module.ocir_gru.order_service_repository_name
}

output "ocir_order_service_repository_url" {
  description = "URL completa do repositório do order-service no OCIR, sem tag."
  value       = module.ocir_gru.order_service_repository_url
}

output "devops_project_id" {
  description = "OCID do projeto OCI DevOps do OCI Pizza."
  value       = module.devops_gru.project_id
}

output "devops_github_connection_id" {
  description = "OCID da conexão externa do OCI DevOps com o GitHub."
  value       = module.devops_gru.github_connection_id
}

output "devops_github_repository_url" {
  description = "URL do repositório GitHub espelhado pelo OCI DevOps."
  value       = module.devops_gru.github_repository_url
}

output "devops_mirrored_repository_id" {
  description = "OCID do repositório do OCI DevOps que espelha o GitHub."
  value       = module.devops_gru.mirrored_repository_id
}

output "devops_mirrored_repository_http_url" {
  description = "URL HTTP do mirror hospedado no OCI Code Repository."
  value       = module.devops_gru.mirrored_repository_http_url
}

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
  description = "Sub-redes privada de serviços e pública de Load Balancer da VCN-SERVICES em São Paulo."
  value       = module.vcn_services_gru.subnet_ids
}

output "vcn_services_vcp_subnet_ids" {
  description = "Sub-redes privada de serviços e pública de Load Balancer da VCN-SERVICES em Vinhedo."
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

output "oci_cache_gru_id" {
  description = "OCID do cluster OCI Cache com Redis 7 em São Paulo."
  value       = module.oci_cache_gru.cluster_id
}

output "oci_cache_vcp_id" {
  description = "OCID do cluster OCI Cache com Redis 7 em Vinhedo."
  value       = module.oci_cache_vcp.cluster_id
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
