#
# vcn-services/locals.tf
#

locals {
  # --------------------------------------------------------------------------
  # VCN-SERVICES - São Paulo (GRU)
  # --------------------------------------------------------------------------
  vcn_services_gru = {
    name              = "vcn-services-gru"
    dns_label         = "vcnservicesgru"
    cidr_block        = "10.74.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f400::/48"
    dhcp_options_name = "dhcp-options-vcn-services-gru"

    # A sub-rede pública recebe o Load Balancer; serviços e Container Instances
    # permanecem na sub-rede privada.
    subnets = {
      loadbalancer = {
        name               = "subnet-services-loadbalancer-gru"
        cidr_block         = "10.74.20.0/24"
        ipv6_cidr_block    = "fd82:44ee:f400:20::/64"
        dns_label          = "loadbalancer"
        prohibit_public_ip = false
      }

      services = {
        name               = "subnet-services-gru"
        cidr_block         = "10.74.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f400:10::/64"
        dns_label          = "services"
        prohibit_public_ip = true
      }
    }

    # O Service Gateway atende serviços OCI; o DRG atende as redes conectadas.
    route_tables = {
      loadbalancer = {
        name = "rt-services-loadbalancer-gru"
        rules = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          target           = "internet"
        }]
      }

      services = {
        name = "rt-services-gru"
        rules = [
          {
            destination      = "all-gru-services-in-oracle-services-network"
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
    }

    # Cada subnet possui sua própria Security List.
    security_lists = {
      loadbalancer = {
        name = "sl-services-loadbalancer-gru"
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
        egress = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          protocol         = "all"
          stateless        = true
        }]
      }

      services = {
        name = "sl-services-gru"
        ingress = [{
          source      = "0.0.0.0/0"
          source_type = "CIDR_BLOCK"
          protocol    = "all"
          stateless   = true
        }]
        egress = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          protocol         = "all"
          stateless        = true
        }]
      }
    }
  }

  # --------------------------------------------------------------------------
  # VCN-SERVICES - Vinhedo (VCP)
  # --------------------------------------------------------------------------
  vcn_services_vcp = {
    name              = "vcn-services-vcp"
    dns_label         = "vcnservicesvcp"
    cidr_block        = "10.84.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f401::/48"
    dhcp_options_name = "dhcp-options-vcn-services-vcp"

    # A sub-rede pública recebe o Load Balancer; serviços e Container Instances
    # permanecem na sub-rede privada.
    subnets = {
      loadbalancer = {
        name               = "subnet-services-loadbalancer-vcp"
        cidr_block         = "10.84.20.0/24"
        ipv6_cidr_block    = "fd82:44ee:f401:20::/64"
        dns_label          = "loadbalancer"
        prohibit_public_ip = false
      }

      services = {
        name               = "subnet-services-vcp"
        cidr_block         = "10.84.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f401:10::/64"
        dns_label          = "services"
        prohibit_public_ip = true
      }
    }

    # O Service Gateway atende serviços OCI; o DRG atende as redes conectadas.
    route_tables = {
      loadbalancer = {
        name = "rt-services-loadbalancer-vcp"
        rules = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          target           = "internet"
        }]
      }

      services = {
        name = "rt-services-vcp"
        rules = [
          {
            destination      = "all-vcp-services-in-oracle-services-network"
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
    }

    # Cada subnet possui sua própria Security List.
    security_lists = {
      loadbalancer = {
        name = "sl-services-loadbalancer-vcp"
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
        egress = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          protocol         = "all"
          stateless        = true
        }]
      }

      services = {
        name = "sl-services-vcp"
        ingress = [{
          source      = "0.0.0.0/0"
          source_type = "CIDR_BLOCK"
          protocol    = "all"
          stateless   = true
        }]
        egress = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          protocol         = "all"
          stateless        = true
        }]
      }
    }
  }

  # Seleciona a configuração correspondente à região da instância do módulo.
  config = var.region_key == "gru" ? local.vcn_services_gru : local.vcn_services_vcp

  # IDs dos gateways usados pelas regras de roteamento.
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
