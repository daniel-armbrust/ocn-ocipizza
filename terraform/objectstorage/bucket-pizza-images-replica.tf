#
# objectstorage/bucket-pizza-images-replica.tf
#

# Bucket de destino, privado, na região de Vinhedo.
# Após a criação da política, o OCI torna este bucket somente leitura.
resource "oci_objectstorage_bucket" "pizza_images_vcp" {
  provider = oci.vcp

  compartment_id = var.compartment_id
  namespace      = data.oci_objectstorage_namespace.this.namespace
  name           = local.bucket_name

  access_type  = "NoPublicAccess"
  storage_tier = "Standard"
  versioning   = "Disabled"
}

# A política replica, de forma assíncrona, novos objetos de GRU para VCP.
resource "oci_objectstorage_replication_policy" "pizza_images" {
  bucket                  = oci_objectstorage_bucket.pizza_images.name
  destination_bucket_name = oci_objectstorage_bucket.pizza_images_vcp.name
  destination_region_name = local.destination_region
  name                    = local.replication_policy_name
  namespace               = data.oci_objectstorage_namespace.this.namespace

  depends_on = [oci_objectstorage_bucket.pizza_images_vcp]
}
