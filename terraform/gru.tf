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

# Cluster OKE Basic em São Paulo com Flannel e Managed Nodes. Somente um dos
# módulos OKE desta região deve permanecer habilitado por vez.
module "oke_gru" {
  source = "./oke/basic-flannel"

  providers = {
    oci = oci.gru
  }

  compartment_id          = var.compartment_id
  region_key              = "gru"
  vcn_id                  = module.vcn_oke_gru.vcn_id
  load_balancer_subnet_id = module.vcn_oke_gru.subnet_ids.loadbalancer
  kube_api_subnet_id      = module.vcn_oke_gru.subnet_ids.kube_api
  worker_subnet_id        = module.vcn_oke_gru.subnet_ids.worker_nodes
  ssh_public_key          = var.oke_worker_ssh_public_key
}

# Cluster OKE Enhanced em São Paulo com OCI VCN-Native Pod Networking e
# Virtual Nodes. O módulo será implementado posteriormente. Para usá-lo,
# comente o módulo Basic acima e descomente este bloco.
# module "oke_gru" {
#   source = "./oke/enhanced-virtual-nodes"
#
#   providers = {
#     oci = oci.gru
#   }
#
#   compartment_id          = var.compartment_id
#   region_key              = "gru"
#   vcn_id                  = module.vcn_oke_gru.vcn_id
#   load_balancer_subnet_id = module.vcn_oke_gru.subnet_ids.loadbalancer
#   kube_api_subnet_id      = module.vcn_oke_gru.subnet_ids.kube_api
#   worker_subnet_id        = module.vcn_oke_gru.subnet_ids.worker_nodes
#   pod_subnet_id           = module.vcn_oke_gru.subnet_ids.pods
# }

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

# MySQL primary em São Paulo. O DB System standalone recebe escritas e é a
# origem da replicação assíncrona para Vinhedo.
module "mysql_gru" {
  source = "./mysql"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
  subnet_id      = module.vcn_db_gru.subnet_ids.mysql
  admin_username = module.vault_gru.mysql_credentials.admin_username
  admin_password = module.vault_gru.mysql_credentials.admin_password
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

# VCN isolada que simula a origem do ambiente on-premises em GRU.
module "vcn_onpremises_gru" {
  source = "./vcn-onpremises"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
}

# Zona DNS privada regional acessível pelas VCNs da aplicação em São Paulo.
module "dns_private_gru" {
  source = "./dns/private-zone"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"

  vcn_ids = {
    firewall = module.vcn_firewall_gru.vcn_id
    oke      = module.vcn_oke_gru.vcn_id
    db       = module.vcn_db_gru.vcn_id
    services = module.vcn_services_gru.vcn_id
  }

  mysql_endpoints = {
    write = module.mysql_gru.endpoint.ip
    read  = module.mysql_gru.endpoint.ip
  }
}

# Cluster OCI Cache primary em São Paulo. Este é o único cluster que aceita
# operações de escrita na topologia active-passive.
module "oci_cache_gru" {
  source = "./oci-cache"

  providers = {
    oci = oci.gru
  }

  compartment_id     = var.compartment_id
  region             = local.regions.gru
  region_key         = "gru"
  vault_region       = local.regions.gru
  vault_scripts_path = abspath("${path.root}/vault/scripts")
  vcn_id             = module.vcn_services_gru.vcn_id
  subnet_id          = module.vcn_services_gru.subnet_ids.services

  depends_on = [module.vault_gru]
}

# Grupo e logs dos microsserviços em São Paulo.
module "logging_gru" {
  source = "./logging"

  providers = {
    oci = oci.gru
  }

  compartment_id    = var.compartment_id
  region_key        = "gru"
  enable_devops_log = true
  devops_project_id = module.devops_gru.project_id
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

  compartment_id          = var.compartment_id
  objectstorage_namespace = data.oci_objectstorage_namespace.ocipizza.namespace
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

# Email Delivery temporariamente desativado. Para reativar, restaure este
# módulo e os registros DKIM comentados em dns.tf.
# module "email_delivery_gru" {
#   source = "./email-delivery"
#
#   providers = {
#     oci = oci.gru
#   }
#
#   compartment_id = var.compartment_id
#   region_key      = "gru"
# }

# Fila OCI Queue de notificações em São Paulo.
module "queue_gru" {
  source = "./queue"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
}

# Topic e assinatura de e-mail usados pelo OCI DevOps em São Paulo.
module "notifications_gru" {
  source = "./notifications"

  providers = {
    oci = oci.gru
  }

  compartment_id     = var.compartment_id
  notification_email = var.notification_email
}

# Vault, chave e Secret persistentes usados pelo OCI DevOps em São Paulo.
module "vault_gru" {
  source = "./vault"

  providers = {
    oci = oci.gru
  }

  compartment_id  = var.compartment_id
  region          = local.regions.gru
  github_pat      = var.github_pat
  ocir_username   = var.ocir_username
  ocir_auth_token = var.ocir_auth_token
}

# Repositórios privados de imagens no OCI Container Registry de São Paulo.
module "ocir_gru" {
  source = "./ocir"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
}

# Repositório Generic dos manifests Kubernetes renderizados para São Paulo.
module "artifact_registry_gru" {
  source = "./artifact-registry"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id
  region_key     = "gru"
}

# Projeto OCI DevOps e conexão externa com o GitHub em São Paulo.
module "devops_gru" {
  source = "./devops"

  providers = {
    oci = oci.gru
  }

  compartment_id          = var.compartment_id
  notification_topic_id   = module.notifications_gru.topic_id
  github_pat_secret_id    = module.vault_gru.github_pat_secret_id
  private_subnet_id       = module.vcn_services_gru.subnet_ids.services
  objectstorage_namespace = data.oci_objectstorage_namespace.ocipizza.namespace

  mysql_primary_region                        = local.regions.gru
  mysql_secondary_region                      = local.regions.vcp
  mysql_primary_host                          = module.mysql_gru.endpoint.ip
  mysql_primary_db_system_id                  = module.mysql_gru.db_system_id
  mysql_secondary_db_system_id                = module.mysql_vcp.db_system_id
  mysql_admin_credentials_secret_id           = module.vault_gru.mysql_admin_credentials_secret_id
  mysql_replication_credentials_secret_id     = module.vault_gru.mysql_replication_credentials_secret_id
  user_service_database_credentials_secret_id = module.vault_gru.user_service_database_credentials_secret_id

  depends_on = [
    oci_identity_policy.ocipizza_devops,
    module.ocir_gru,
  ]
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
    services = module.vcn_services_gru.vcn_id
  }
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
  ssh_public_key = var.firewall_ssh_public_key
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
  ssh_public_key = var.firewall_ssh_public_key
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
