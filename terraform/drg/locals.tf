#
# drg/locals.tf
#

locals {
  # Configuração nominal do DRG em São Paulo.
  drg_gru = {
    name = "drg-gru"

    # Redes das VCNs que devem encaminhar o tráfego para o firewall.
    spoke_cidr_blocks = [
      "10.71.0.0/16", # VCN-OKE
      "10.72.0.0/16", # VCN-DB
      "10.73.0.0/16", # VCN-CI
      "10.74.0.0/16", # VCN-SERVICES
    ]
  }

  # Configuração nominal do DRG em Vinhedo.
  drg_vcp = {
    name = "drg-vcp"

    # Redes das VCNs que devem encaminhar o tráfego para o firewall.
    spoke_cidr_blocks = [
      "10.81.0.0/16", # VCN-OKE
      "10.82.0.0/16", # VCN-DB
      "10.83.0.0/16", # VCN-CI
      "10.84.0.0/16", # VCN-SERVICES
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
    ci = {
      name   = "drg-attachment-ci-${var.region_key}"
      vcn_id = var.vcn_ids.ci
    }
    services = {
      name   = "drg-attachment-services-${var.region_key}"
      vcn_id = var.vcn_ids.services
    }
  }
}
