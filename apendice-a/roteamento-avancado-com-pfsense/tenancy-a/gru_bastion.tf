#
# gru_bastion.tf
#   - Bastion da região GRU.
#

resource "oci_bastion_bastion" "gru_bastion" {
    provider = oci.gru

    compartment_id = var.compartment_id
    name = "BastionGru"
    bastion_type = "standard"
    client_cidr_block_allow_list = [local.my_public_ip]
    target_subnet_id = oci_core_subnet.gru_vcn-firewall_subnprv-lan.id
}