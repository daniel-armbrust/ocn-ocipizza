#
# oke/outputs.tf
#

output "cluster_id" {
  description = "OCID do cluster OKE regional."
  value       = oci_containerengine_cluster.this.id
}

output "cluster_name" {
  description = "Nome do cluster OKE regional."
  value       = oci_containerengine_cluster.this.name
}

output "node_pool_id" {
  description = "OCID do node pool regional."
  value       = oci_containerengine_node_pool.this.id
}

output "kubernetes_version" {
  description = "Versão do Kubernetes provisionada no cluster."
  value       = var.kubernetes_version
}

output "private_endpoint" {
  description = "Endpoint privado do Kubernetes API."
  value       = oci_containerengine_cluster.this.endpoints[0].private_endpoint
}
