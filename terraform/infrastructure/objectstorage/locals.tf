#
# objectstorage/locals.tf
#

locals {
  # Nome utilizado pelo pizza-service para armazenar as imagens das pizzas.
  bucket_name = "pizza-images"

  # Região que receberá a cópia dos objetos enviados ao bucket de GRU.
  destination_region = "sa-vinhedo-1"

  # Nome da política de replicação configurada no bucket de origem.
  replication_policy_name = "pizza-images-vcp"
}
