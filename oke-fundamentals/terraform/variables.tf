#
# variables.tf
#

variable "tenancy_id" {
  description = "OCID da tenancy, utilizada como Root Compartment pelos recursos IAM."
  type        = string

  validation {
    condition     = startswith(var.tenancy_id, "ocid1.tenancy.")
    error_message = "tenancy_id deve ser um OCID de tenancy válido."
  }
}

variable "compartment_id" {
  description = "OCID do compartment que receberá a VCN-OKE."
  type        = string
}

variable "public_access_cidr" {
  description = "CIDR IPv4 público autorizado a acessar o Kubernetes API Server."
  type        = string

  validation {
    condition     = can(cidrhost(var.public_access_cidr, 0)) && can(regex("^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+/32$", var.public_access_cidr))
    error_message = "public_access_cidr deve ser um endereço IPv4 público individual no formato x.x.x.x/32."
  }
}

variable "oci_config_profile" {
  description = "Profile usado no arquivo de configuração do OCI."
  type        = string
  default     = "DEFAULT"
}

variable "kubernetes_version" {
  description = "Versão do Kubernetes usada pelo control plane e pelo node pool."
  type        = string
  default     = "v1.34.10"
}

variable "worker_image_id" {
  description = "OCID opcional de uma imagem Oracle Linux x86 compatível."
  type        = string
  default     = null
}
