#
# objectstorage/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda os buckets de imagens."
  type        = string
}

variable "objectstorage_namespace" {
  description = "Namespace do Object Storage da tenancy usado pelos buckets e pela replicação."
  type        = string

  validation {
    condition     = length(trimspace(var.objectstorage_namespace)) > 0
    error_message = "objectstorage_namespace não pode ser vazio."
  }
}
