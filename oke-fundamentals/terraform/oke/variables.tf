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

variable "worker_image_id" {
  description = "OCID opcional de uma imagem x86 compatível com a versão do Kubernetes."
  type        = string
  default     = null
}
