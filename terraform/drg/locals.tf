#
# drg/locals.tf
#

locals {
  # Todas as redes que devem ser submetidas à inspeção do firewall regional.
  # A tabela de ingresso do attachment da VCN-FIREWALL precisa reconhecer
  # destinos locais e remotos para encaminhá-los ao NLB da região atual.
  inspection_cidr_blocks = [
    "10.70.0.0/16", # VCN-FIREWALL-GRU
    "10.71.0.0/16", # VCN-OKE-GRU
    "10.72.0.0/16", # VCN-DB-GRU
    "10.74.0.0/16", # VCN-SERVICES-GRU
    "10.80.0.0/16", # VCN-FIREWALL-VCP
    "10.81.0.0/16", # VCN-OKE-VCP
    "10.82.0.0/16", # VCN-DB-VCP
    "10.84.0.0/16", # VCN-SERVICES-VCP
  ]

  # Configuração nominal do DRG em São Paulo.
  drg_gru = {
    name = "drg-gru"

    # Spokes locais anunciados ao RPC por meio do firewall de GRU.
    spoke_cidr_blocks = [
      "10.71.0.0/16", # VCN-OKE-GRU
      "10.72.0.0/16", # VCN-DB-GRU
      "10.74.0.0/16", # VCN-SERVICES-GRU
    ]
  }

  # Configuração nominal do DRG em Vinhedo.
  drg_vcp = {
    name = "drg-vcp"

    # Spokes locais anunciados ao RPC por meio do firewall de VCP.
    spoke_cidr_blocks = [
      "10.81.0.0/16", # VCN-OKE-VCP
      "10.82.0.0/16", # VCN-DB-VCP
      "10.84.0.0/16", # VCN-SERVICES-VCP
    ]
  }

  # Seleciona a configuração correspondente à instância regional do módulo.
  config = var.region_key == "gru" ? local.drg_gru : local.drg_vcp

  # Cada VCN possui um attachment próprio no DRG regional.
  attachments = {
    firewall = {
      name   = "drg-attachment-firewall-${var.region_key}"
      vcn_id = var.vcn_ids.firewall
    }

    oke = {
      name   = "drg-attachment-oke-${var.region_key}"
      vcn_id = var.vcn_ids.oke
    }

    db = {
      name   = "drg-attachment-db-${var.region_key}"
      vcn_id = var.vcn_ids.db
    }

    services = {
      name   = "drg-attachment-services-${var.region_key}"
      vcn_id = var.vcn_ids.services
    }

  }
}
