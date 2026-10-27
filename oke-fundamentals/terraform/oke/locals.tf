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

  # FLANNEL_OVERLAY mantém a rede dos pods sobreposta à VCN e dispensa uma
  # sub-rede adicional para endereços de pods.
  cni_type = "FLANNEL_OVERLAY"

  # Configuração didática dos três worker nodes x86 AMD.
  node_shape     = "VM.Standard.E4.Flex"
  node_ocpus     = 2
  node_memory_gb = 4
  node_pool_size = 3
}
