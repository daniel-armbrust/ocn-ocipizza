#
# oci-cache/outputs.tf
#

output "cluster_id" {
  description = "OCID do cluster regional OCI Cache com Redis 7."
  value       = oci_redis_redis_cluster.this.id
}

output "cluster_role" {
  description = "Papel efetivo do cluster na replicação cross-region."
  value       = oci_redis_redis_cluster.this.cluster_role
}

output "config_set_id" {
  description = "OCID do Configuration Set regional usado pelo cluster."
  value       = oci_redis_oci_cache_config_set.this.id
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
  description = "Nome regional do cluster OCI Cache com Redis 7."
  value       = oci_redis_redis_cluster.this.display_name
}
