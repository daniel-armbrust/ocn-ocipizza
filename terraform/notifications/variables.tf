#
# notifications/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospedará o Topic do OCI Notifications."
  type        = string
}

variable "notification_email" {
  description = "Endereço de e-mail inscrito no Topic usado pelo OCI DevOps."
  type        = string

  validation {
    condition     = can(regex("^[^@[:space:]]+@[^@[:space:]]+\\.[^@[:space:]]+$", var.notification_email))
    error_message = "notification_email deve conter um endereço de e-mail válido."
  }
}
