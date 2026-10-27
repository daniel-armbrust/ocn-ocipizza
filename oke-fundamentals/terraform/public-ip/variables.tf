#
# public-ip/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que receberá o endereço IP reservado."
  type        = string
}
