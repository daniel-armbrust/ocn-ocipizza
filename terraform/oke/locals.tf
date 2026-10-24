#
# oke/locals.tf
#

locals {
  # Nomes regionais tornam os recursos facilmente identificáveis na Console.
  cluster_name   = "oke-${var.region_key}"
  node_pool_name = "oke-workers-${var.region_key}"

  # FLANNEL mantém os pods sobre a rede overlay do Kubernetes. Com isso,
  # a VCN-OKE precisa somente das sub-redes já dedicadas ao API, LB e workers.
  cni_type = "FLANNEL_OVERLAY"

  # Cada worker A1 Flex recebe exatamente 3 OCPUs e 6 GB de RAM.
  node_shape     = "VM.Standard.A1.Flex"
  node_ocpus     = 3
  node_memory_gb = 6
  node_pool_size = 2
}
