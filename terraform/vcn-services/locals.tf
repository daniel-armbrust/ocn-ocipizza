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

    # Sub-rede privada para serviços internos da plataforma.
    subnets = {
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

    # Tráfego totalmente liberado, conforme solicitado para esta VCN didática.
    security_lists = {
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

    # Sub-rede privada para serviços internos da plataforma.
    subnets = {
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

    # Tráfego totalmente liberado, conforme solicitado para esta VCN didática.
    security_lists = {
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
    service = oci_core_service_gateway.this.id
  }

  route_table_ids = {
    for key, route_table in oci_core_route_table.this : key => route_table.id
  }

  security_list_ids = {
    for key, security_list in oci_core_security_list.this : key => security_list.id
  }
}
