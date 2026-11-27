#
# dns/private-zone/variables.tf
#

variable "compartment_id" {
  description = "OCID do compartment que hospeda os recursos do DNS privado."
  type        = string
}

variable "region_key" {
  description = "Identificador curto da região onde a zona privada será criada."
  type        = string

  validation {
    condition     = contains(["gru", "vcp"], var.region_key)
    error_message = "region_key deve ser gru ou vcp."
  }
}

variable "vcn_ids" {
  description = "Mapa das VCNs cujos resolvers devem consultar a zona privada."
  type        = map(string)

  validation {
    condition = (
      length(var.vcn_ids) == 4
      && contains(keys(var.vcn_ids), "firewall")
      && contains(keys(var.vcn_ids), "oke")
      && contains(keys(var.vcn_ids), "db")
      && contains(keys(var.vcn_ids), "services")
    )
    error_message = "vcn_ids deve conter somente as chaves firewall, oke, db e services."
  }
}

variable "mysql_endpoints" {
  description = "Endereços IPv4 privados dos endpoints MySQL de escrita e leitura."
  type = object({
    write = string
    read  = string
  })

  validation {
    condition = (
      can(cidrhost("${var.mysql_endpoints.write}/32", 0))
      && can(cidrhost("${var.mysql_endpoints.read}/32", 0))
    )
    error_message = "mysql_endpoints.write e mysql_endpoints.read devem conter endereços IPv4 válidos."
  }
}

variable "redis_fqdn" {
  description = "FQDN do endpoint primário do OCI Cache em GRU."
  type        = string

  validation {
    condition     = length(trimspace(var.redis_fqdn)) > 0
    error_message = "redis_fqdn não pode ser vazio."
  }
}

variable "queue_messages_endpoints" {
  description = "URLs dos endpoints regionais do OCI Queue em GRU e VCP."
  type = object({
    gru = string
    vcp = string
  })

  validation {
    condition = alltrue([
      for endpoint in values(var.queue_messages_endpoints) :
      startswith(trimspace(endpoint), "https://") &&
      length(split("/", trimprefix(trimspace(endpoint), "https://"))[0]) > 0
    ])
    error_message = "queue_messages_endpoints.gru e queue_messages_endpoints.vcp devem conter URLs HTTPS válidas."
  }
}
