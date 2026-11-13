#
# public-ip/outputs.tf
#

output "public_ip_id" {
  description = "OCID do endereço IP público reservado."
  value       = oci_core_public_ip.load_balancer.id
}

output "public_ip_address" {
  description = "Endereço IPv4 público reservado para o load balancer."
  value       = oci_core_public_ip.load_balancer.ip_address
}
