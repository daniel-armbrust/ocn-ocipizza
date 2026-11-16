#
# devops/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospedará os recursos do OCI DevOps."
  type        = string
}

variable "notification_topic_id" {
  description = "OCID do Topic usado pelas notificações do projeto OCI DevOps."
  type        = string
}

variable "github_pat_secret_id" {
  description = "OCID do Secret no OCI Vault que contém o PAT do GitHub."
  type        = string
}
