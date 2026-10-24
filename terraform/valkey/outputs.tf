#
# valkey/outputs.tf
#

output "cluster_id" {
  description = "OCID do cluster regional OCI Cache."
  value       = oci_redis_redis_cluster.this.id
}

output "primary_endpoint_ip_address" {
  description = "IP privado do endpoint primário do cluster."
  value       = oci_redis_redis_cluster.this.primary_endpoint_ip_address
}

output "primary_fqdn" {
  description = "FQDN do endpoint primário do cluster."
  value       = oci_redis_redis_cluster.this.primary_fqdn
}

output "display_name" {
  description = "Nome regional do cluster OCI Cache."
  value       = oci_redis_redis_cluster.this.display_name
}
