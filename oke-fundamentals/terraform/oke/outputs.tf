#
# oke/outputs.tf
#

output "cluster_id" {
  description = "OCID do cluster OKE."
  value       = oci_containerengine_cluster.this.id
}

output "cluster_name" {
  description = "Nome do cluster OKE."
  value       = oci_containerengine_cluster.this.name
}

output "node_pool_id" {
  description = "OCID do node pool."
  value       = oci_containerengine_node_pool.this.id
}

output "kubernetes_version" {
  description = "Versão do Kubernetes provisionada."
  value       = var.kubernetes_version
}

output "public_endpoint" {
  description = "Endpoint público do Kubernetes API Server."
  value       = oci_containerengine_cluster.this.endpoints[0].public_endpoint
}
