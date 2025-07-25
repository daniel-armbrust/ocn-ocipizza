#
# vcp_bastion.tf
#   - Bastion da região VCP.
#

resource "oci_bastion_bastion" "vcp_bastion_vcn-firewall_subnprv-lan" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    name = "BastionVcpVcnFirewall"
    bastion_type = "STANDARD"
    client_cidr_block_allow_list = [local.my_public_ip]
    target_subnet_id = oci_core_subnet.vcp_vcn-firewall_subnprv-lan.id
}