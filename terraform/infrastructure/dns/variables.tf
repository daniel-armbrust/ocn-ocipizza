#
# dns/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda a zona DNS pública."
  type        = string
}

variable "load_balancer_public_ips" {
  description = "Endereços IPv4 reservados para os load balancers regionais."
  type        = map(string)

  validation {
    condition = (
      length(var.load_balancer_public_ips) == 2
      && contains(keys(var.load_balancer_public_ips), "gru")
      && contains(keys(var.load_balancer_public_ips), "vcp")
    )
    error_message = "load_balancer_public_ips deve conter somente as chaves gru e vcp."
  }
}

variable "email_dkim_records" {
  description = "Registros CNAME DKIM gerados pelo Email Delivery regional."
  type = map(object({
    domain = string
    value  = string
  }))
}
