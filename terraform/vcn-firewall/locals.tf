#
# vcn-firewall/locals.tf
#

locals {
  # --------------------------------------------------------------------------
  # Configuração regional da VCN-FIREWALL em São Paulo (GRU).
  # --------------------------------------------------------------------------
  vcn_firewall_gru = {
    region            = "sa-saopaulo-1"
    name              = "vcn-firewall-gru"
    dns_label         = "vcnfirewallgru"
    cidr_block        = "10.70.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f000::/48"
    dhcp_options_name = "dhcp-options-vcn-firewall-gru"

    # Uma sub-rede privada hospeda o NLB e outra hospeda as VNICs do firewall.
    subnets = {
      nlb = {
        name               = "subnet-firewall-nlb-gru"
        cidr_block         = "10.70.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f000:10::/64"
        dns_label          = "nlb"
        prohibit_public_ip = true
      }

      firewall = {
        name               = "subnet-firewall-gru"
        cidr_block         = "10.70.20.0/24"
        ipv6_cidr_block    = "fd82:44ee:f000:20::/64"
        dns_label          = "firewall"
        prohibit_public_ip = true
      }
    }

    # A sub-rede do NLB encaminha todo o tráfego para o DRG. A sub-rede do
    # firewall usa o SGW para serviços OCI, o DRG para spokes e o NGW para a
    # saída padrão à Internet.
    route_tables = {
      nlb = {
        name = "rt-firewall-nlb-gru"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "drg"
          }
        ]
      }

      firewall = {
        name = "rt-firewall-gru"
        rules = concat(
          [
            {
              destination      = "all-gru-services-in-oracle-services-network"
              destination_type = "SERVICE_CIDR_BLOCK"
              target           = "service"
            }
          ],
          [
            for destination in [
              "10.71.0.0/16",
              "10.72.0.0/16",
              "10.73.0.0/16",
              "10.74.0.0/16",
              "10.81.0.0/16",
              "10.82.0.0/16",
              "10.83.0.0/16",
              "10.84.0.0/16"
              ] : {
              destination      = destination
              destination_type = "CIDR_BLOCK"
              target           = "drg"
            }
          ],
          [
            {
              destination      = "0.0.0.0/0"
              destination_type = "CIDR_BLOCK"
              target           = "nat"
            }
          ]
        )
      }
    }

    # O firewall deixou de receber tráfego diretamente da Internet; as duas
    # sub-redes permanecem privadas e permissivas nesta etapa didática.
    security_lists = {
      nlb = {
        name = "sl-firewall-nlb-gru"
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

      firewall = {
        name = "sl-firewall-gru"
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
  # Configuração regional da VCN-FIREWALL em Vinhedo (VCP).
  # --------------------------------------------------------------------------
  vcn_firewall_vcp = {
    region            = "sa-vinhedo-1"
    name              = "vcn-firewall-vcp"
    dns_label         = "vcnfirewallvcp"
    cidr_block        = "10.80.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f001::/48"
    dhcp_options_name = "dhcp-options-vcn-firewall-vcp"

    # Sub-rede privada do NLB e sub-rede privada das VNICs do firewall.
    subnets = {
      nlb = {
        name               = "subnet-firewall-nlb-vcp"
        cidr_block         = "10.80.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f001:10::/64"
        dns_label          = "nlb"
        prohibit_public_ip = true
      }

      firewall = {
        name               = "subnet-firewall-vcp"
        cidr_block         = "10.80.20.0/24"
        ipv6_cidr_block    = "fd82:44ee:f001:20::/64"
        dns_label          = "firewall"
        prohibit_public_ip = true
      }
    }

    route_tables = {
      nlb = {
        name = "rt-firewall-nlb-vcp"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "drg"
          }
        ]
      }

      firewall = {
        name = "rt-firewall-vcp"
        rules = concat(
          [
            {
              destination      = "all-vcp-services-in-oracle-services-network"
              destination_type = "SERVICE_CIDR_BLOCK"
              target           = "service"
            }
          ],
          [
            for destination in [
              "10.71.0.0/16",
              "10.72.0.0/16",
              "10.73.0.0/16",
              "10.74.0.0/16",
              "10.81.0.0/16",
              "10.82.0.0/16",
              "10.83.0.0/16",
              "10.84.0.0/16"
              ] : {
              destination      = destination
              destination_type = "CIDR_BLOCK"
              target           = "drg"
            }
          ],
          [
            {
              destination      = "0.0.0.0/0"
              destination_type = "CIDR_BLOCK"
              target           = "nat"
            }
          ]
        )
      }
    }

    security_lists = {
      nlb = {
        name = "sl-firewall-nlb-vcp"
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

      firewall = {
        name = "sl-firewall-vcp"
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
}

locals {
  # Seleciona a configuração correspondente à instância regional do módulo.
  config = var.region_key == "gru" ? local.vcn_firewall_gru : local.vcn_firewall_vcp
}

locals {
  # IDs derivados dos recursos são centralizados para manter as associações
  # entre sub-redes, tabelas de rotas e Security Lists explícitas.
  gateway_ids = {
    nat     = oci_core_nat_gateway.this.id
    service = oci_core_service_gateway.this.id
  }

  route_table_ids = {
    for key, route_table in oci_core_route_table.this : key => route_table.id
  }

  security_list_ids = {
    for key, security_list in oci_core_security_list.this : key => security_list.id
  }
}
