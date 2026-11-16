#
# objectstorage/outputs.tf
#

output "bucket_name" {
  description = "Nome do bucket principal de imagens em São Paulo."
  value       = oci_objectstorage_bucket.pizza_images.name
}

output "bucket_id" {
  description = "OCID do bucket principal de imagens em São Paulo."
  value       = oci_objectstorage_bucket.pizza_images.bucket_id
}

output "replica_bucket_id" {
  description = "OCID do bucket de destino em Vinhedo."
  value       = oci_objectstorage_bucket.pizza_images_vcp.bucket_id
}

output "replication_policy_id" {
  description = "Identificador da política de replicação entre as regiões."
  value       = oci_objectstorage_replication_policy.pizza_images.id
}
