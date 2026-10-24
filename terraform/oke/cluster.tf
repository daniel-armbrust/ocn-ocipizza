#
# oke/cluster.tf
#

resource "oci_containerengine_cluster" "this" {
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = local.cluster_name
  type               = "BASIC_CLUSTER"
  vcn_id             = var.vcn_id

  # O endpoint do Kubernetes API fica privado na sub-rede própria do OKE.
  endpoint_config {
    is_public_ip_enabled = false
    subnet_id            = var.kube_api_subnet_id
  }

  # Os Load Balancers públicos do OKE usam exclusivamente a sub-rede de LB.
  options {
    service_lb_subnet_ids = [var.load_balancer_subnet_id]
  }

  # FLANNEL_OVERLAY mantém os pods em uma rede overlay e usa somente as três
  # sub-redes já criadas para API, Load Balancers e worker nodes.
  cluster_pod_network_options {
    cni_type = local.cni_type
  }
}
