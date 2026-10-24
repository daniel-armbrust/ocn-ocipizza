#
# nlb/outputs.tf
#

output "network_load_balancer_id" {
  description = "OCID do Network Load Balancer privado."
  value       = oci_network_load_balancer_network_load_balancer.this.id
}

output "subnet_id" {
  description = "OCID da sub-rede privada onde o NLB foi criado."
  value       = var.subnet_id
}

output "private_ip" {
  description = "Endereço IPv4 privado atribuído ao NLB."
  value       = data.oci_core_private_ips.network_load_balancer.private_ips[0].ip_address
}

output "private_ip_id" {
  description = "OCID do IP privado do NLB, usado como próximo salto de rota."
  value       = data.oci_core_private_ips.network_load_balancer.private_ips[0].id
}
