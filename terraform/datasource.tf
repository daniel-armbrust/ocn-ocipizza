#
# datasource.tf
#

# O namespace é único por tenancy e é compartilhado pelos módulos que usam
# Object Storage e OCI Container Registry.
data "oci_objectstorage_namespace" "ocipizza" {
  provider       = oci.gru
  compartment_id = var.compartment_id
}
