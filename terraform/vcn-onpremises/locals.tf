#
# vcn-onpremises/locals.tf
#

locals {
  # CIDRs didáticos reservados para representar a rede on-premises em GRU.
  vcn = {
    name              = "vcn-onpremises-gru"
    dns_label         = "vcnonpremisesgru"
    cidr_block        = "10.90.0.0/16"
    ipv6_cidr_block   = "fd82:44ee:f900::/48"
    dhcp_options_name = "dhcp-options-vcn-onpremises-gru"
  }

  # A única sub-rede é pública para representar o segmento externo do
  # ambiente on-premises usado nos testes de conectividade.
  subnet = {
    name               = "subnet-onpremises-gru"
    cidr_block         = "10.90.10.0/24"
    ipv6_cidr_block    = "fd82:44ee:f900:10::/64"
    dns_label          = "onpremises"
    prohibit_public_ip = false
  }

  # A rota padrão usa o Internet Gateway para representar a rede de origem.
  # A conexão VPN será modelada posteriormente, fora desta VCN isolada.
  route_rules = [
    {
      destination      = "0.0.0.0/0"
      destination_type = "CIDR_BLOCK"
      target           = "internet"
    }
  ]

  # Security List stateful: nenhum ingresso é permitido e todo o egress é
  # mantido com estado para respostas das conexões iniciadas internamente.
  ingress_rules = []
  egress_rules = [{
    destination      = "0.0.0.0/0"
    destination_type = "CIDR_BLOCK"
    protocol         = "all"
    stateless        = false
  }]

  gateway_ids = {
    internet = oci_core_internet_gateway.this.id
  }
}
