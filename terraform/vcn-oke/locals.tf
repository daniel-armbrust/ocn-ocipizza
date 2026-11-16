#
# vcn-oke/locals.tf
#

locals {
  # --------------------------------------------------------------------------
  # VCN-OKE - São Paulo (GRU)
  # --------------------------------------------------------------------------

  # A configuração regional é explícita para facilitar a documentação da
  # topologia multi-região e a comparação com Vinhedo.
  vcn_oke_gru = {
    # Identidade e endereçamento principal da VCN.
    name              = "vcn-oke-gru"
    dns_label         = "vcnokegru"
    cidr_block        = "10.71.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f100::/48"
    dhcp_options_name = "dhcp-options-vcn-oke-gru"

    # ------------------------------------------------------------------------
    # A sub-rede de load balancers é pública; workers e API permanecem
    # privados para que o tráfego de saída seja controlado pelo DRG.
    # ------------------------------------------------------------------------
    subnets = {
      # Load Balancers públicos do OKE.
      loadbalancer = {
        name               = "subnet-oke-loadbalancer-gru"
        cidr_block         = "10.71.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f100:10::/64"
        dns_label          = "loadbalancer"
        prohibit_public_ip = false
      }

      # Nós de trabalho que executam os pods da aplicação.
      worker_nodes = {
        name               = "subnet-oke-worker-gru"
        cidr_block         = "10.71.20.0/23"
        ipv6_cidr_block    = "fd82:44ee:f100:20::/64"
        dns_label          = "workers"
        prohibit_public_ip = true
      }

      # Sub-rede privada do Kubernetes API Server.
      kube_api = {
        name               = "subnet-oke-kube-api-gru"
        cidr_block         = "10.71.30.0/24"
        ipv6_cidr_block    = "fd82:44ee:f100:30::/64"
        dns_label          = "kubeapi"
        prohibit_public_ip = true
      }
    }

    # Cada sub-rede possui sua própria Route Table.
    route_tables = {
      loadbalancer = {
        name = "rt-oke-loadbalancer-gru"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "internet"
          }
        ]
      }

      # Tabela de rotas dos nós de trabalho.
      worker_nodes = {
        name = "rt-oke-worker-gru"
        rules = [
          {
            # Os workers de GRU acessam os serviços OCI pelo SGW local.
            destination      = "service"
            destination_type = "SERVICE_CIDR_BLOCK"
            target           = "service"
          },
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "drg"
          }
        ]
      }

      # Tabela de rotas do Kubernetes API Server.
      kube_api = {
        name = "rt-oke-kube-api-gru"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "drg"
          }
        ]
      }
    }

    # Cada sub-rede possui sua própria Security List.
    security_lists = {
      loadbalancer = {
        name = "sl-oke-loadbalancer-gru"
        ingress = [
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "6"
            stateless   = true
            tcp_options = { min = 80, max = 80 }
          },
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "6"
            stateless   = true
            tcp_options = { min = 443, max = 443 }
          }
        ]
        egress = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            protocol         = "all"
            stateless        = true
          }
        ]
      }

      # Security List dos nós de trabalho.
      worker_nodes = {
        name = "sl-oke-worker-gru"
        ingress = [
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "all"
            stateless   = true
          }
        ]
        egress = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            protocol         = "all"
            stateless        = true
          }
        ]
      }

      # Security List do Kubernetes API Server.
      kube_api = {
        name = "sl-oke-kube-api-gru"
        ingress = [
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "all"
            stateless   = true
          }
        ]
        egress = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            protocol         = "all"
            stateless        = true
          }
        ]
      }
    }
  }

  # --------------------------------------------------------------------------
  # VCN-OKE - Vinhedo (VCP)
  # --------------------------------------------------------------------------
  # Os valores abaixo são independentes dos valores de GRU, principalmente
  # os CIDRs e os nomes dos recursos regionais.
  vcn_oke_vcp = {
    # Identidade e endereçamento principal da VCN.
    name              = "vcn-oke-vcp"
    dns_label         = "vcnokevcp"
    cidr_block        = "10.81.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f101::/48"
    dhcp_options_name = "dhcp-options-vcn-oke-vcp"

    # A sub-rede de load balancers é pública; workers e API permanecem
    # privados para que o tráfego de saída seja controlado pelo DRG.
    subnets = {
      # Load Balancers públicos do OKE.
      loadbalancer = {
        name               = "subnet-oke-loadbalancer-vcp"
        cidr_block         = "10.81.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f101:10::/64"
        dns_label          = "loadbalancer"
        prohibit_public_ip = false
      }

      # Nós de trabalho que executam os pods da aplicação.
      worker_nodes = {
        name               = "subnet-oke-worker-vcp"
        cidr_block         = "10.81.20.0/23"
        ipv6_cidr_block    = "fd82:44ee:f101:20::/64"
        dns_label          = "workers"
        prohibit_public_ip = true
      }

      # Sub-rede privada do Kubernetes API Server.
      kube_api = {
        name               = "subnet-oke-kube-api-vcp"
        cidr_block         = "10.81.30.0/24"
        ipv6_cidr_block    = "fd82:44ee:f101:30::/64"
        dns_label          = "kubeapi"
        prohibit_public_ip = true
      }
    }

    # Cada sub-rede possui sua própria Route Table.
    route_tables = {
      loadbalancer = {
        name = "rt-oke-loadbalancer-vcp"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "internet"
          }
        ]
      }

      # Tabela de rotas dos nós de trabalho.
      worker_nodes = {
        name = "rt-oke-worker-vcp"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "drg"
          }
        ]
      }

      # Tabela de rotas do Kubernetes API Server.
      kube_api = {
        name = "rt-oke-kube-api-vcp"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "drg"
          }
        ]
      }
    }

    # Cada sub-rede possui sua própria Security List.
    security_lists = {
      loadbalancer = {
        name = "sl-oke-loadbalancer-vcp"
        ingress = [
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "6"
            stateless   = true
            tcp_options = { min = 80, max = 80 }
          },
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "6"
            stateless   = true
            tcp_options = { min = 443, max = 443 }
          }
        ]
        egress = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            protocol         = "all"
            stateless        = true
          }
        ]
      }

      # Security List dos nós de trabalho.
      worker_nodes = {
        name = "sl-oke-worker-vcp"
        ingress = [
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "all"
            stateless   = true
          }
        ]
        egress = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            protocol         = "all"
            stateless        = true
          }
        ]
      }

      # Security List do Kubernetes API Server.
      kube_api = {
        name = "sl-oke-kube-api-vcp"
        ingress = [
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "all"
            stateless   = true
          }
        ]
        egress = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            protocol         = "all"
            stateless        = true
          }
        ]
      }
    }
  }

  # Seleciona a configuração correspondente à instância regional do módulo.
  # O root module chama este módulo uma vez por região.
  config = var.region_key == "gru" ? local.vcn_oke_gru : local.vcn_oke_vcp

  gateway_ids = {
    internet = oci_core_internet_gateway.this.id
    service  = oci_core_service_gateway.this.id
  }

  route_table_ids = {
    for key, route_table in oci_core_route_table.this : key => route_table.id
  }

  security_list_ids = {
    for key, security_list in oci_core_security_list.this : key => security_list.id
  }
}
