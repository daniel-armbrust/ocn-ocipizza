#
# outputs.tf
#

output "oke_cluster_id" {
  description = "OCID do cluster OKE."
  value       = module.oke.cluster_id
}

output "oke_node_pool_id" {
  description = "OCID do node pool do OKE."
  value       = module.oke.node_pool_id
}

output "oke_kubernetes_version" {
  description = "Versão do Kubernetes provisionada."
  value       = module.oke.kubernetes_version
}

output "oke_public_endpoint" {
  description = "Endpoint público do Kubernetes API Server."
  value       = module.oke.public_endpoint
}

output "oke_cni_type" {
  description = "Tipo de CNI configurado no cluster OKE."
  value       = module.oke.cni_type
}

output "oke_cluster_type" {
  description = "Tipo do cluster OKE."
  value       = module.oke.cluster_type
}

output "dns_zone_id" {
  description = "OCID da zona DNS pública ocipizza.com.br."
  value       = module.dns_public.zone_id
}

output "dns_nameservers" {
  description = "Nameservers autoritativos que devem ser configurados no registrador do domínio."
  value       = module.dns_public.nameservers
}

output "dns_domain_name" {
  description = "Nome da zona DNS pública."
  value       = module.dns_public.domain_name
}

output "load_balancer_public_ip_id" {
  description = "OCID do endereço IP público reservado para o Load Balancer."
  value       = module.public_ip_load_balancer.public_ip_id
}

output "load_balancer_public_ip" {
  description = "Endereço IPv4 publicado em lb.ocipizza.com.br."
  value       = module.public_ip_load_balancer.public_ip_address
}

output "oke_worker_nodes_dynamic_group_id" {
  description = "OCID do Dynamic Group que contém os worker nodes do OKE."
  value       = oci_identity_dynamic_group.oke_worker_nodes.id
}

output "oke_worker_nodes_ocir_policy_id" {
  description = "OCID da policy que permite aos worker nodes ler imagens do OCIR."
  value       = oci_identity_policy.oke_worker_nodes_ocir.id
}
