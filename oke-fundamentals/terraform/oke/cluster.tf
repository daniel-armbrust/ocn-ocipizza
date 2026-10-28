#
# oke/cluster.tf
#

resource "oci_containerengine_cluster" "this" {
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = local.cluster_name
  type               = local.cluster_type
  vcn_id             = var.vcn_id

  # O endpoint público é criado na sub-rede kube_api. A Security List dessa
  # sub-rede limita o acesso externo ao CIDR informado pelo usuário.
  endpoint_config {
    is_public_ip_enabled = true
    subnet_id            = var.kube_api_subnet_id
  }

  # Services do tipo LoadBalancer utilizam exclusivamente a sub-rede pública
  # reservada para os Load Balancers do OKE.
  options {
    service_lb_subnet_ids = [var.load_balancer_subnet_id]
  }

  cluster_pod_network_options {
    cni_type = local.cni_type
  }

  lifecycle {
    precondition {
      condition = (
        var.cni_type != "OCI_VCN_IP_NATIVE"
        || (var.pod_subnet_id != null && trimspace(var.pod_subnet_id) != "")
      )
      error_message = "pod_subnet_id é obrigatório quando cni_type for OCI_VCN_IP_NATIVE."
    }
  }
}
