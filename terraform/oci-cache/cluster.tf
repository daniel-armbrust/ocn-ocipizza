#
# oci-cache/cluster.tf
#

# Cluster privado OCI Cache com engine Redis 7.
resource "oci_redis_redis_cluster" "this" {
  compartment_id     = var.compartment_id
  display_name       = local.display_name
  node_count         = local.node_count
  node_memory_in_gbs = local.node_memory_in_gbs
  software_version   = local.software_version
  subnet_id          = var.subnet_id
  cluster_mode       = local.cluster_mode
}

# Remove a Security List criada pelo OCI Cache fora do controle do Terraform,
# depois que o cluster estiver disponível.
# TODO: verificar periodicamente se o OCI Cache deixou de criar a
# redis-security-list. Este recurso e o script são um workaround temporário e
# devem ser removidos quando o serviço corrigir esse comportamento.
resource "terraform_data" "delete_redis_security_list" {
  input = {
    compartment_id = var.compartment_id
    region         = var.region
    script         = "${path.module}/scripts/delete-seclist.sh"
    subnet_id      = var.subnet_id
    vcn_id         = var.vcn_id
  }

  triggers_replace = oci_redis_redis_cluster.this.id

  provisioner "local-exec" {
    command = "bash ${self.input.script}"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
      SUBNET_ID      = self.input.subnet_id
      VCN_ID         = self.input.vcn_id
    }
  }

  depends_on = [oci_redis_redis_cluster.this]
}
