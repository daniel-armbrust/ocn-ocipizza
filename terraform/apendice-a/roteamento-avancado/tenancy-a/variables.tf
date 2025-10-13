#
# variables.tf
#

variable "api_fingerprint" {
    description = "Fingerprint da chave privada que será utilizada para a comunicação com as APIs do OCI."
    type = string
}

variable "api_private_key_path" {
    description = "Caminho para o arquivo da chave privada."
    type = string
}

variable "tenancy_id" {
    description = "OCID do Tenancy."
    type = string
}

variable "user_id" {
    description = "OCID do usuário que será utilizado para interagir com as APIs do OCI."
    type = string
}

variable "compartment_id" {
    description = "OCID do compartimento que será utilizado para armazenar os recursos que serão criados."
    type = string  
}