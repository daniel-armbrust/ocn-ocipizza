#
# nlb/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospedará o NLB."
  type        = string
}

variable "region_key" {
  description = "Chave da região do NLB: gru ou vcp."
  type        = string
}

variable "subnet_id" {
  description = "OCID da sub-rede privada destinada ao NLB."
  type        = string
}

variable "firewall_ips" {
  description = "Endereços IPv4 privados dos firewalls que receberão o tráfego."
  type        = list(string)

  validation {
    condition     = length(var.firewall_ips) == 2
    error_message = "O NLB deve receber exatamente dois firewalls como backends."
  }
}

variable "listener_ports" {
  description = "Portas publicadas pelo NLB. O valor 0 representa qualquer porta."
  type        = set(number)
  default     = [0]
}

variable "health_check_port" {
  description = "Porta TCP usada para verificar a saúde dos firewalls."
  type        = number
  default     = 22
}
