#
# gru.tf
#

# VCN-FIREWALL em São Paulo.
module "vcn_firewall_gru" {
  source = "./vcn-firewall"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  drg_id         = module.drg_gru.drg_id
}

# VCN-OKE em São Paulo.
module "vcn_oke_gru" {
  source = "./vcn-oke"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  drg_id         = module.drg_gru.drg_id
}

# Cluster OKE em São Paulo: API privado, Load Balancers públicos e workers
# privados, cada componente usando a sub-rede correspondente da VCN-OKE.
module "oke_gru" {
  source = "./oke"

  providers = {
    oci = oci.gru
  }

  compartment_id          = var.compartment_id
  region_key              = "gru"
  vcn_id                  = module.vcn_oke_gru.vcn_id
  load_balancer_subnet_id = module.vcn_oke_gru.subnet_ids.loadbalancer
  kube_api_subnet_id      = module.vcn_oke_gru.subnet_ids.kube_api
  worker_subnet_id        = module.vcn_oke_gru.subnet_ids.worker_nodes
}

# VCN-DB em São Paulo.
module "vcn_db_gru" {
  source = "./vcn-db"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  drg_id         = module.drg_gru.drg_id
}

# VCN-SERVICES em São Paulo.
module "vcn_services_gru" {
  source = "./vcn-services"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  drg_id         = module.drg_gru.drg_id
}

# Cluster OCI Cache Valkey em São Paulo.
module "valkey_gru" {
  source = "./valkey"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  subnet_id      = module.vcn_services_gru.subnet_ids.services
}

# Grupo e logs dos microsserviços em São Paulo.
module "logging_gru" {
  source = "./logging"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
}

# Tabelas NoSQL da aplicação em GRU com réplicas Global Active em VCP.
module "nosql_tables" {
  source = "./nosql"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
}

# Bucket privado de imagens em GRU, com réplica regional em VCP.
module "objectstorage_buckets" {
  source = "./objectstorage"

  providers = {
    oci     = oci.gru
    oci.vcp = oci.vcp
  }

  compartment_id = var.compartment_id
}

# IP público reservado para lb-gru.ocipizza.com.br.
module "public_ip_load_balancer_gru" {
  source = "./public-ip"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
}

# Email Delivery em GRU, incluindo domínio, DKIM e remetente aprovado.
module "email_delivery_gru" {
  source = "./email-delivery"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
}

# Fila OCI Queue de notificações em São Paulo.
module "queue_gru" {
  source = "./queue"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
}

# DRG regional e attachments das VCNs de São Paulo.
module "drg_gru" {
  source = "./drg"

  providers = {
    oci = oci.gru
  }

  compartment_id               = var.compartment_id
  region_key                   = "gru"
  firewall_trust_private_ip_id = module.compute_firewall_gru.trust_private_ip_id
  nlb_private_ip_id            = module.nlb_firewall_gru.private_ip_id
  vcn_ids = {
    firewall = module.vcn_firewall_gru.vcn_id
    oke      = module.vcn_oke_gru.vcn_id
    db       = module.vcn_db_gru.vcn_id
    ci       = module.vcn_ci_gru.vcn_id
    services = module.vcn_services_gru.vcn_id
  }
}

# VCN-CI em São Paulo.
module "vcn_ci_gru" {
  source = "./vcn-ci"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  drg_id         = module.drg_gru.drg_id
}

# Compute Firewall 1 em São Paulo, com uma VNIC privada.
module "compute_firewall_gru" {
  source = "./compute-firewall"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  subnet_ids     = module.vcn_firewall_gru.subnet_ids
  ssh_public_key = local.firewall_ssh_public_key
}

# Segundo Compute Firewall em São Paulo, usado como backend do NLB.
module "compute_firewall_gru_2" {
  source = "./compute-firewall"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  firewall_index = 2
  subnet_ids     = module.vcn_firewall_gru.subnet_ids
  ssh_public_key = local.firewall_ssh_public_key
}

# NLB privado que distribui o tráfego TCP para os dois firewalls de GRU.
module "nlb_firewall_gru" {
  source = "./nlb"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  subnet_id      = module.vcn_firewall_gru.subnet_ids.nlb
  firewall_ips = [
    module.compute_firewall_gru.trust_private_ip,
    module.compute_firewall_gru_2.trust_private_ip
  ]
}
