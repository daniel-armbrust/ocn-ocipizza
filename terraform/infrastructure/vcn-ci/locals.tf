#
# vcn-ci/locals.tf
#

locals {
  # --------------------------------------------------------------------------
  # VCN-CI - São Paulo (GRU)
  # --------------------------------------------------------------------------
  vcn_ci_gru = {
    name              = "vcn-ci-gru"
    dns_label         = "vcncigru"
    cidr_block        = "10.73.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f300::/48"
    dhcp_options_name = "dhcp-options-vcn-ci-gru"

    # O load balancer é público; as Container Instances permanecem privadas.
    subnets = {
      loadbalancer = {
        name               = "subnet-ci-loadbalancer-gru"
        cidr_block         = "10.73.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f300:10::/64"
        dns_label          = "loadbalancer"
        prohibit_public_ip = false
      }

      container_instances = {
        name               = "subnet-ci-container-gru"
        cidr_block         = "10.73.20.0/23"
        ipv6_cidr_block    = "fd82:44ee:f300:20::/64"
        dns_label          = "containers"
        prohibit_public_ip = true
      }
    }

    # Cada sub-rede possui uma Route Table própria.
    route_tables = {
      loadbalancer = {
        name = "rt-ci-loadbalancer-gru"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "internet"
          }
        ]
      }

      container_instances = {
        name = "rt-ci-container-gru"
        rules = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          target           = "drg"
        }]
      }
    }

    # Cada sub-rede possui uma Security List própria.
    security_lists = {
      loadbalancer = {
        name = "sl-ci-loadbalancer-gru"
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

      container_instances = {
        name = "sl-ci-container-gru"
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
  # VCN-CI - Vinhedo (VCP)
  # --------------------------------------------------------------------------
  vcn_ci_vcp = {
    name              = "vcn-ci-vcp"
    dns_label         = "vcncivcp"
    cidr_block        = "10.83.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f301::/48"
    dhcp_options_name = "dhcp-options-vcn-ci-vcp"

    # O load balancer é público; as Container Instances permanecem privadas.
    subnets = {
      loadbalancer = {
        name               = "subnet-ci-loadbalancer-vcp"
        cidr_block         = "10.83.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f301:10::/64"
        dns_label          = "loadbalancer"
        prohibit_public_ip = false
      }

      container_instances = {
        name               = "subnet-ci-container-vcp"
        cidr_block         = "10.83.20.0/23"
        ipv6_cidr_block    = "fd82:44ee:f301:20::/64"
        dns_label          = "containers"
        prohibit_public_ip = true
      }
    }

    # Cada sub-rede possui uma Route Table própria.
    route_tables = {
      loadbalancer = {
        name = "rt-ci-loadbalancer-vcp"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "internet"
          }
        ]
      }

      container_instances = {
        name = "rt-ci-container-vcp"
        rules = [{
          destination      = "0.0.0.0/0"
          destination_type = "CIDR_BLOCK"
          target           = "drg"
        }]
      }
    }

    # Cada sub-rede possui uma Security List própria.
    security_lists = {
      loadbalancer = {
        name = "sl-ci-loadbalancer-vcp"
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

      container_instances = {
        name = "sl-ci-container-vcp"
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

  # Seleciona a configuração correspondente à instância regional do módulo.
  config = var.region_key == "gru" ? local.vcn_ci_gru : local.vcn_ci_vcp

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
