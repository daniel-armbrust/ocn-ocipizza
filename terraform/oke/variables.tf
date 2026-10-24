#
# oke/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que receberá o cluster OKE."
  type        = string
}

variable "region_key" {
  description = "Chave da região do cluster: gru ou vcp."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}

variable "vcn_id" {
  description = "OCID da VCN-OKE onde o cluster será criado."
  type        = string
}

variable "load_balancer_subnet_id" {
  description = "OCID da sub-rede pública destinada aos Load Balancers do OKE."
  type        = string
}

variable "kube_api_subnet_id" {
  description = "OCID da sub-rede privada do endpoint do Kubernetes API."
  type        = string
}

variable "worker_subnet_id" {
  description = "OCID da sub-rede privada dos worker nodes."
  type        = string
}

variable "kubernetes_version" {
  description = <<-EOT
    Versão do Kubernetes usada pelo control plane e pelos worker nodes.
    O padrão acompanha duas versões menores atrás da linha estável atual
    documentada para este exemplo didático.
  EOT
  type        = string
  default     = "v1.34.10"
}

variable "worker_image_id" {
  description = "OCID opcional da imagem ARM dos worker nodes; se nulo, o OKE escolhe uma imagem compatível."
  type        = string
  default     = null
}

variable "ssh_public_key" {
  description = "Chave pública opcional instalada nos worker nodes."
  type        = string
  default     = null
}
