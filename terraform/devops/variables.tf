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

variable "private_subnet_id" {
  description = "OCID da subnet privada usada pelos Managed Build stages do OCI DevOps."
  type        = string
}

variable "objectstorage_namespace" {
  description = "Namespace do Object Storage da tenancy usado para compor URLs do OCIR."
  type        = string

  validation {
    condition     = length(trimspace(var.objectstorage_namespace)) > 0
    error_message = "objectstorage_namespace não pode ser vazio."
  }
}

variable "mysql_primary_region" {
  description = "Região do MySQL primary usada pela pipeline de bootstrap."
  type        = string
  default     = "sa-saopaulo-1"
}

variable "mysql_secondary_region" {
  description = "Região do MySQL secondary usada pela pipeline de bootstrap."
  type        = string
  default     = "sa-vinhedo-1"
}

variable "mysql_primary_host" {
  description = "Nome DNS privado usado para acessar o MySQL primary."
  type        = string
  default     = "mysql-write.ocipizza.internal"

  validation {
    condition     = length(trimspace(var.mysql_primary_host)) > 0
    error_message = "mysql_primary_host não pode ser vazio."
  }
}

variable "mysql_primary_db_system_id" {
  description = "OCID do MySQL DB System primary."
  type        = string
}

variable "mysql_secondary_db_system_id" {
  description = "OCID do MySQL DB System secondary."
  type        = string
}

variable "mysql_admin_credentials_secret_id" {
  description = "OCID do Secret com as credenciais administrativas do MySQL."
  type        = string
}

variable "mysql_replication_credentials_secret_id" {
  description = "OCID do Secret com as credenciais de replicação do MySQL."
  type        = string
}

variable "user_service_database_credentials_secret_id" {
  description = "OCID do Secret com as credenciais de banco do user-service."
  type        = string
}
