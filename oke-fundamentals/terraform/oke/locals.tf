#
# oke/locals.tf
#

locals {
  cluster_name   = "oke-fundamentals"
  node_pool_name = "oke-fundamentals-workers"

  # Somente a chave pública é lida pelo Terraform e enviada ao OKE. O par de
  # chaves permanece local no diretório keys e não deve ser versionado.
  worker_ssh_public_key_path = "${path.module}/keys/worker-nodes.pub"
  worker_ssh_public_key = fileexists(local.worker_ssh_public_key_path) ? trimspace(
    file(local.worker_ssh_public_key_path)
  ) : null

  # Converte o nome amigável do tipo de cluster no valor esperado pelo OKE.
  cluster_types = {
    BASIC    = "BASIC_CLUSTER"
    ENHANCED = "ENHANCED_CLUSTER"
  }

  # O tipo de CNI já utiliza diretamente o valor esperado pela API do OKE.
  cni_type     = var.cni_type
  cluster_type = local.cluster_types[var.cluster_type]

  # Configuração didática dos três worker nodes x86 AMD.
  node_shape     = "VM.Standard.E4.Flex"
  node_ocpus     = 2
  node_memory_gb = 4
  node_pool_size = 3
}
