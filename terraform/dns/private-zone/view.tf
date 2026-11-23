#
# dns/private-zone/view.tf
#

# View regional compartilhada pelos resolvers das VCNs da aplicação.
resource "oci_dns_view" "this" {
  compartment_id = var.compartment_id
  display_name   = local.private_view_name
  scope          = "PRIVATE"
}
