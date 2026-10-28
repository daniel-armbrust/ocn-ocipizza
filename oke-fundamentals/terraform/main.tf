#
# main.tf
#

module "vcn_oke" {
  source = "./vcn-oke"

  providers = {
    oci = oci.gru
  }

  compartment_id     = var.compartment_id
  public_access_cidr = var.public_access_cidr
}

module "oke" {
  source = "./oke"

  providers = {
    oci = oci.gru
  }

  compartment_id          = var.compartment_id
  vcn_id                  = module.vcn_oke.vcn_id
  load_balancer_subnet_id = module.vcn_oke.subnet_ids["loadbalancer"]
  kube_api_subnet_id      = module.vcn_oke.subnet_ids["kube_api"]
  worker_subnet_id        = module.vcn_oke.subnet_ids["worker_nodes"]
  kubernetes_version      = var.kubernetes_version
  cni_type                = var.cni_type
  pod_subnet_id           = var.pod_subnet_id
  cluster_type            = var.cluster_type
  worker_image_id         = var.worker_image_id
}

# IP público reservado para o Load Balancer exposto em lb.ocipizza.com.br.
module "public_ip_load_balancer" {
  source = "./public-ip"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
}

# Zona DNS pública global utilizada pelo laboratório OKE Fundamentals.
module "dns_public" {
  source = "./dns"

  providers = {
    oci = oci.gru
  }

  compartment_id          = var.compartment_id
  load_balancer_public_ip = module.public_ip_load_balancer.public_ip_address
}
