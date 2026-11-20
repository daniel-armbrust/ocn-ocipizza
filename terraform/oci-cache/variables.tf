#
# oci-cache/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda o cluster OCI Cache."
  type        = string
}

variable "region_key" {
  description = "Chave curta da região usada no nome do cluster."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}

variable "region" {
  description = "Região OCI usada pelas chamadas da OCI CLI para limpeza da Security List automática."
  type        = string
}

variable "primary_cluster_id" {
  description = "OCID do cluster primary de GRU. Deve ser null em GRU e informado para o secondary em VCP."
  type        = string
  default     = null
  nullable    = true
}

variable "subnet_id" {
  description = "OCID da sub-rede privada onde o cluster será criado."
  type        = string
}

variable "vcn_id" {
  description = "OCID da VCN usada para localizar a Security List criada automaticamente pelo OCI Cache."
  type        = string
}
