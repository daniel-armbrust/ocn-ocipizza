#
# dns/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda a zona DNS pública."
  type        = string
}

variable "load_balancer_public_ip" {
  description = "Endereço IPv4 reservado publicado no registro A do Load Balancer."
  type        = string
}
