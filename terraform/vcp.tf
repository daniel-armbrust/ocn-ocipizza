#
# vcp.tf
#

# VCN-FIREWALL em Vinhedo.
module "vcn_firewall_vcp" {
  source = "./vcn-firewall"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  drg_id         = module.drg_vcp.drg_id
}

# VCN-OKE em Vinhedo.
module "vcn_oke_vcp" {
  source = "./vcn-oke"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  drg_id         = module.drg_vcp.drg_id
}

# Cluster OKE em Vinhedo com a mesma separação de sub-redes de GRU.
module "oke_vcp" {
  source = "./oke"

  providers = {
    oci = oci.vcp
  }

  compartment_id          = var.compartment_id
  region_key              = "vcp"
  vcn_id                  = module.vcn_oke_vcp.vcn_id
  load_balancer_subnet_id = module.vcn_oke_vcp.subnet_ids.loadbalancer
  kube_api_subnet_id      = module.vcn_oke_vcp.subnet_ids.kube_api
  worker_subnet_id        = module.vcn_oke_vcp.subnet_ids.worker_nodes
}

# VCN-DB em Vinhedo.
module "vcn_db_vcp" {
  source = "./vcn-db"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  drg_id         = module.drg_vcp.drg_id
}

# VCN-SERVICES em Vinhedo.
module "vcn_services_vcp" {
  source = "./vcn-services"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  drg_id         = module.drg_vcp.drg_id
}

# IP público reservado para lb-vcp.ocipizza.com.br.
module "public_ip_load_balancer_vcp" {
  source = "./public-ip"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
}

# Cluster OCI Cache Valkey em Vinhedo.
module "valkey_vcp" {
  source = "./valkey"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  subnet_id      = module.vcn_services_vcp.subnet_ids.services
}

# Grupo e logs dos microsserviços em Vinhedo.
module "logging_vcp" {
  source = "./logging"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
}

# Email Delivery em VCP, incluindo domínio, DKIM e remetente aprovado.
module "email_delivery_vcp" {
  source = "./email-delivery"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
}

# Fila OCI Queue de notificações em Vinhedo.
module "queue_vcp" {
  source = "./queue"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
}

# DRG regional e attachments das VCNs de Vinhedo.
module "drg_vcp" {
  source = "./drg"

  providers = {
    oci = oci.vcp
  }

  compartment_id               = var.compartment_id
  region_key                   = "vcp"
  firewall_trust_private_ip_id = module.compute_firewall_vcp.trust_private_ip_id
  nlb_private_ip_id            = module.nlb_firewall_vcp.private_ip_id
  vcn_ids = {
    firewall = module.vcn_firewall_vcp.vcn_id
    oke      = module.vcn_oke_vcp.vcn_id
    db       = module.vcn_db_vcp.vcn_id
    ci       = module.vcn_ci_vcp.vcn_id
    services = module.vcn_services_vcp.vcn_id
  }
}

# VCN-CI em Vinhedo.
module "vcn_ci_vcp" {
  source = "./vcn-ci"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  drg_id         = module.drg_vcp.drg_id
}

# Compute Firewall 1 em Vinhedo, com uma VNIC privada.
module "compute_firewall_vcp" {
  source = "./compute-firewall"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  subnet_ids     = module.vcn_firewall_vcp.subnet_ids
  ssh_public_key = local.firewall_ssh_public_key
}

# Segundo Compute Firewall em Vinhedo, usado como backend do NLB.
module "compute_firewall_vcp_2" {
  source = "./compute-firewall"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  firewall_index = 2
  subnet_ids     = module.vcn_firewall_vcp.subnet_ids
  ssh_public_key = local.firewall_ssh_public_key
}

# NLB privado que distribui o tráfego TCP para os dois firewalls de VCP.
module "nlb_firewall_vcp" {
  source = "./nlb"

  providers = {
    oci = oci.vcp
  }

  compartment_id = var.compartment_id
  region_key     = "vcp"
  subnet_id      = module.vcn_firewall_vcp.subnet_ids.nlb
  firewall_ips = [
    module.compute_firewall_vcp.trust_private_ip,
    module.compute_firewall_vcp_2.trust_private_ip
  ]
}
