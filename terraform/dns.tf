#
# dns.tf
#

# Zona DNS pública global da aplicação OCI Pizza.
module "dns_public" {
  source = "./dns"

  providers = {
    oci = oci.gru
  }

  compartment_id = var.compartment_id

  # Email Delivery está desativado. Ao reativar os módulos regionais, restaure:
  # gru = module.email_delivery_gru.dkim_record
  # vcp = module.email_delivery_vcp.dkim_record
  email_dkim_records = {}

  load_balancer_public_ips = {
    gru = module.public_ip_load_balancer_gru.public_ip_address
    vcp = module.public_ip_load_balancer_vcp.public_ip_address
  }
}
