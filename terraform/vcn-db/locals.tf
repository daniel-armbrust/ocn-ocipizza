#
# vcn-db/locals.tf
#

locals {
  # --------------------------------------------------------------------------
  # VCN-DB - São Paulo (GRU)
  # --------------------------------------------------------------------------
  vcn_db_gru = {
    # Identidade e endereçamento principal da VCN.
    name              = "vcn-db-gru"
    dns_label         = "vcndbgru"
    cidr_block        = "10.72.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f200::/48"
    dhcp_options_name = "dhcp-options-vcn-db-gru"

    # Sub-rede privada destinada ao MySQL HeatWave.
    subnets = {
      mysql = {
        name               = "subnet-db-mysql-gru"
        cidr_block         = "10.72.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f200:10::/64"
        dns_label          = "mysql"
        prohibit_public_ip = true
      }
    }

    # Todo o tráfego da sub-rede privada segue para o DRG.
    route_tables = {
      mysql = {
        name = "rt-db-mysql-gru"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "drg"
          }
        ]
      }
    }

    # Security List exclusiva da sub-rede do banco.
    security_lists = {
      mysql = {
        name = "sl-db-mysql-gru"
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
  # VCN-DB - Vinhedo (VCP)
  # --------------------------------------------------------------------------
  vcn_db_vcp = {
    # Identidade e endereçamento principal da VCN.
    name              = "vcn-db-vcp"
    dns_label         = "vcndbvcp"
    cidr_block        = "10.82.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f201::/48"
    dhcp_options_name = "dhcp-options-vcn-db-vcp"

    # Sub-rede privada destinada ao MySQL HeatWave.
    subnets = {
      mysql = {
        name               = "subnet-db-mysql-vcp"
        cidr_block         = "10.82.10.0/24"
        ipv6_cidr_block    = "fd82:44ee:f201:10::/64"
        dns_label          = "mysql"
        prohibit_public_ip = true
      }
    }

    # Todo o tráfego da sub-rede privada segue para o DRG.
    route_tables = {
      mysql = {
        name = "rt-db-mysql-vcp"
        rules = [
          {
            destination      = "0.0.0.0/0"
            destination_type = "CIDR_BLOCK"
            target           = "drg"
          }
        ]
      }
    }

    # Security List exclusiva da sub-rede do banco.
    security_lists = {
      mysql = {
        name = "sl-db-mysql-vcp"
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

  # Seleciona a configuração correspondente à região da instância do módulo.
  config = var.region_key == "gru" ? local.vcn_db_gru : local.vcn_db_vcp

  route_table_ids = {
    for key, route_table in oci_core_route_table.this : key => route_table.id
  }

  security_list_ids = {
    for key, security_list in oci_core_security_list.this : key => security_list.id
  }
}
