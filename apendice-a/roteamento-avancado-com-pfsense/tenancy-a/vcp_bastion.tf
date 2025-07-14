#
# gru_bastion.tf
#   - Bastion da região VCP.
#

resource "oci_bastion_bastion" "vcp_bastion" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    name = "BastionVcp"
    bastion_type = "standard"
    client_cidr_block_allow_list = [local.my_public_ip]
    target_subnet_id = oci_core_subnet.vcp_vcn-firewall_subnprv-lan.id
}