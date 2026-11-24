#
# devops/bootstrap/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que contém os recursos usados pelos bootstraps."
  type        = string
}

variable "project_id" {
  description = "OCID do projeto OCI DevOps que hospedará as pipelines de bootstrap."
  type        = string
}

variable "repository_id" {
  description = "OCID do Code Repository espelhado que contém os scripts de bootstrap."
  type        = string
}

variable "repository_url" {
  description = "URL HTTP do Code Repository espelhado que contém os scripts de bootstrap."
  type        = string

  validation {
    condition     = length(trimspace(var.repository_url)) > 0
    error_message = "repository_url não pode ser vazia."
  }
}

variable "repository_branch" {
  description = "Branch do Code Repository consumida pelos Managed Build stages."
  type        = string
  default     = "main"

  validation {
    condition     = length(trimspace(var.repository_branch)) > 0
    error_message = "repository_branch não pode ser vazia."
  }
}

variable "private_subnet_id" {
  description = "OCID da subnet privada usada pelos Managed Build stages de bootstrap."
  type        = string
}

variable "mysql_primary_region" {
  description = "Região do MySQL primary usada como padrão pela Build Pipeline."
  type        = string
  default     = "sa-saopaulo-1"
}

variable "mysql_secondary_region" {
  description = "Região do MySQL secondary usada como padrão pela Build Pipeline."
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
  description = "OCID do Secret com as credenciais do usuário de replicação."
  type        = string
}

variable "user_service_database_credentials_secret_id" {
  description = "OCID do Secret com as credenciais de banco do user-service."
  type        = string
}
