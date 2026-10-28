#
# oke/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que receberá o cluster OKE."
  type        = string
}

variable "vcn_id" {
  description = "OCID da VCN onde o cluster OKE será criado."
  type        = string
}

variable "load_balancer_subnet_id" {
  description = "OCID da sub-rede pública destinada aos Load Balancers do OKE."
  type        = string
}

variable "kube_api_subnet_id" {
  description = "OCID da sub-rede pública destinada ao Kubernetes API Server."
  type        = string
}

variable "worker_subnet_id" {
  description = "OCID da sub-rede privada destinada aos worker nodes."
  type        = string
}

variable "kubernetes_version" {
  description = "Versão do Kubernetes usada pelo control plane e pelo node pool."
  type        = string
  default     = "v1.34.10"
}

variable "cni_type" {
  description = "Plugin de rede dos pods conforme a API do OKE: OCI_VCN_IP_NATIVE ou FLANNEL_OVERLAY."
  type        = string

  validation {
    condition     = contains(["OCI_VCN_IP_NATIVE", "FLANNEL_OVERLAY"], var.cni_type)
    error_message = "cni_type deve ser OCI_VCN_IP_NATIVE ou FLANNEL_OVERLAY."
  }
}

variable "pod_subnet_id" {
  description = "OCID da sub-rede dos pods, obrigatório quando cni_type for OCI_VCN_IP_NATIVE."
  type        = string
  default     = null
  nullable    = true
}

variable "cluster_type" {
  description = "Tipo do cluster OKE: BASIC ou ENHANCED."
  type        = string

  validation {
    condition     = contains(["BASIC", "ENHANCED"], var.cluster_type)
    error_message = "cluster_type deve ser BASIC ou ENHANCED."
  }
}

variable "worker_image_id" {
  description = "OCID opcional de uma imagem x86 compatível com a versão do Kubernetes."
  type        = string
  default     = null
}
