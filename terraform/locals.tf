#
# locals.tf
#

locals {
  # Regiões utilizadas pela composição multi-região da infraestrutura.
  regions = {
    gru = "sa-saopaulo-1"
    vcp = "sa-vinhedo-1"
  }

  # A chave pública local é instalada no metadata da instância pelo cloud-init.
  # A chave privada correspondente nunca é enviada ao OCI.
  firewall_ssh_public_key = file(
    "${path.root}/compute-firewall/keys/firewall.pub"
  )
}
