#
# vcn-oke/locals.tf
#

locals {
  vcn_cidr_block = "10.71.0.0/16"

  # Configuração central da VCN usada pelo laboratório OKE em São Paulo.
  # Os valores de rede ficam agrupados para evitar configurações dispersas
  # entre os recursos Terraform do módulo.
  config = {
    # Identidade e endereçamento principal da VCN.
    name              = "vcn-oke"
    dns_label         = "vcnoke"
    cidr_block        = local.vcn_cidr_block
    ipv6_cidr_block   = "fd82:44ee:f100::/48"
    dhcp_options_name = "dhcp-options-vcn-oke"

    # Cada função do OKE possui uma sub-rede regional dedicada, com sua própria
    # Route Table e Security List.
    subnets = {

      # Sub-rede pública usada pelos Load Balancers da aplicação.
      loadbalancer = {
        name               = "subnet-oke-loadbalancer"
        cidr_block         = "10.71.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f100:10::/64"
        dns_label          = "loadbalancer"
        prohibit_public_ip = false
      }

      # Sub-rede privada dos worker nodes. As VNICs não recebem IP público.
      worker_nodes = {
        name               = "subnet-oke-worker"
        cidr_block         = "10.71.20.0/23"
        ipv6_cidr_block    = "fd82:44ee:f100:20::/64"
        dns_label          = "workers"
        prohibit_public_ip = true
      }

      # Sub-rede pública do endpoint do Kubernetes API Server.
      kube_api = {
        name               = "subnet-oke-kube-api"
        cidr_block         = "10.71.30.0/24"
        ipv6_cidr_block    = "fd82:44ee:f100:30::/64"
        dns_label          = "kubeapi"
        prohibit_public_ip = false
      }
    }

    # As chaves das Route Tables correspondem às chaves das sub-redes.
    route_tables = {

      # Acesso direto à internet pelo Internet Gateway.
      loadbalancer = {
        name = "rt-oke-loadbalancer"
        rules = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          target           = "internet"
        }]
      }

      # Acesso aos serviços OCI pelo Service Gateway e aos demais destinos
      # pelo NAT Gateway, mantendo os nós sem exposição pública direta.
      worker_nodes = {
        name = "rt-oke-worker"
        rules = [
          {
            destination      = "service"
            destination_type = "SERVICE_CIDR_BLOCK"
            target           = "service"
          },
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "nat"
          }
        ]
      }

      # Acesso direto à internet pelo Internet Gateway.
      kube_api = {
        name = "rt-oke-kube-api"
        rules = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          target           = "internet"
        }]
      }
    }

    # Security Lists associadas individualmente às três sub-redes. Todas as
    # regras são stateful para que o tráfego de resposta seja permitido
    # automaticamente pela OCI.
    security_lists = {

      # HTTP e HTTPS são públicos para permitir o acesso às aplicações
      # expostas pelos Load Balancers do OKE.
      loadbalancer = {
        name = "sl-oke-loadbalancer"
        ingress = [
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "6"
            stateless   = false
            tcp_options = { min = 80, max = 80 }
          },
          {
            source      = "0.0.0.0/0"
            source_type = "CIDR_BLOCK"
            protocol    = "6"
            stateless   = false
            tcp_options = { min = 443, max = 443 }
          }
        ]

        egress = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          protocol         = "all"
          stateless        = false
        }]
      }

      # Conforme o escopo do laboratório, permite todo o tráfego IPv4 de
      # entrada e saída. A ausência de IP público mantém a sub-rede privada.
      worker_nodes = {
        name = "sl-oke-worker"
        ingress = [{
          source      = "0.0.0.0/0"
          source_type = "CIDR_BLOCK"
          protocol    = "all"
          stateless   = false
        }]

        egress = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          protocol         = "all"
          stateless        = false
        }]
      }

      # A porta 6443 é aceita do IPv4 /32 informado pelo usuário. O tráfego
      # interno originado na própria VCN é permitido para viabilizar a
      # comunicação entre o control plane e os demais componentes do OKE.
      kube_api = {
        name = "sl-oke-kube-api"
        ingress = [
          {
            source      = var.public_access_cidr
            source_type = "CIDR_BLOCK"
            protocol    = "6"
            stateless   = false
            tcp_options = { min = 6443, max = 6443 }
          },
          {
            source      = local.vcn_cidr_block
            source_type = "CIDR_BLOCK"
            protocol    = "all"
            stateless   = false
          }
        ]

        egress = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          protocol         = "all"
          stateless        = false
        }]
      }

    }
  }

  # Traduz os nomes usados nas rotas para os OCIDs dos gateways do módulo.
  gateway_ids = {
    internet = oci_core_internet_gateway.this.id
    nat      = oci_core_nat_gateway.this.id
    service  = oci_core_service_gateway.this.id
  }

  # Associa os OCIDs das Route Tables às respectivas chaves de sub-rede.
  route_table_ids = {
    for key, route_table in oci_core_route_table.this : key => route_table.id
  }

  # Associa os OCIDs das Security Lists às respectivas chaves de sub-rede.
  security_list_ids = {
    for key, security_list in oci_core_security_list.this : key => security_list.id
  }
}
