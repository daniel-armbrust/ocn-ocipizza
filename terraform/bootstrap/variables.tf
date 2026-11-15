#
# variables.tf
#

variable "resource_manager_compartment_id" {
  description = "OCID do compartment onde o stack do Resource Manager será criado."
  type        = string
}

variable "tenancy_id" {
  description = "OCID da tenancy onde o dynamic group da OCI Pizza será criado."
  type        = string
}

variable "iam_dynamic_group_name" {
  description = "Nome do dynamic group que reúne as instâncias da OCI Pizza."
  type        = string
  default     = "ocipizza-instances"
}

variable "iam_policy_name" {
  description = "Nome da policy que autoriza os Instance Principals da OCI Pizza."
  type        = string
  default     = "ocipizza-instance-principals"
}

variable "infrastructure_deployer_group_id" {
  description = "OCID do grupo IAM cujos usuários executarão os jobs do stack de infraestrutura."
  type        = string
}

variable "infrastructure_deployer_policy_name" {
  description = "Nome da policy que autoriza o grupo executor a provisionar a infraestrutura da OCI Pizza."
  type        = string
  default     = "ocipizza-infrastructure-deployer"
}

variable "service_principals_policy_name" {
  description = "Nome da policy que autoriza os serviços gerenciados utilizados pelo OCI Pizza."
  type        = string
  default     = "ocipizza-service-principals"
}

variable "resource_manager_stack_name" {
  description = "Nome do stack de infraestrutura no Resource Manager."
  type        = string
  default     = "ocipizza-infrastructure"
}

variable "resource_manager_repository_url" {
  description = "URL do repositório Git que contém a configuração Terraform."
  type        = string
  default     = "https://github.com/daniel-armbrust/ocn-ocipizza.git"
}

variable "resource_manager_repository_branch" {
  description = "Branch do repositório utilizada pelo stack."
  type        = string
  default     = "main"
}

variable "resource_manager_working_directory" {
  description = "Diretório do repositório que contém o root module da infraestrutura."
  type        = string
  default     = "terraform/infrastructure"
}

variable "resource_manager_terraform_version" {
  description = "Versão do Terraform utilizada pelo stack."
  type        = string
  default     = "1.5.x"
}

variable "infrastructure_compartment_id" {
  description = "OCID do compartment onde os recursos da infraestrutura serão provisionados."
  type        = string
}

variable "firewall_ssh_public_key" {
  description = "Chave pública SSH instalada nas instâncias de firewall."
  type        = string
}

variable "oke_worker_ssh_public_key" {
  description = "Chave pública SSH instalada nos worker nodes do OKE."
  type        = string
}
