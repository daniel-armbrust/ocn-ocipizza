#
# nlb/datasource.tf
#

# O NLB recebe um IP privado atribuído pelo serviço. O objeto de IP retornado
# pelo NLB é consultado novamente para obter o OCID necessário quando ele for
# usado como próximo salto de uma tabela de rotas da VCN.
data "oci_core_private_ips" "network_load_balancer" {
  subnet_id = var.subnet_id
  ip_address = one([
    for address in oci_network_load_balancer_network_load_balancer.this.ip_addresses : address.ip_address
    if !address.is_public
  ])

  depends_on = [oci_network_load_balancer_network_load_balancer.this]
}
