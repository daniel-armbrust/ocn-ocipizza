#
# objectstorage/bucket-pizza-images.tf
#

# Bucket principal, privado, na região de São Paulo.
resource "oci_objectstorage_bucket" "pizza_images" {
  compartment_id = var.compartment_id
  namespace      = data.oci_objectstorage_namespace.this.namespace
  name           = local.bucket_name

  # Somente chamadas autenticadas podem acessar os objetos.
  access_type  = "NoPublicAccess"
  storage_tier = "Standard"
  versioning   = "Disabled"
}
