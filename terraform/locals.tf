#
# locals.tf
#

locals {
  # Regiões utilizadas pela composição multi-região da infraestrutura.
  regions = {
    gru = "sa-saopaulo-1"
    vcp = "sa-vinhedo-1"
  }
}
