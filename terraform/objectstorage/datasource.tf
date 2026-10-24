#
# objectstorage/datasource.tf
#

# O namespace é único por tenancy e é reutilizado nos dois buckets regionais.
data "oci_objectstorage_namespace" "this" {}
