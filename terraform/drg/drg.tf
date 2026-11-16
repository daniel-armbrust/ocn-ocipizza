#
# drg/drg.tf
#

# O DRG é o hub regional da topologia Hub-and-Spoke.
resource "oci_core_drg" "this" {
  compartment_id = var.compartment_id
  display_name   = local.config.name
}
