#
# compute-firewall/datasource.tf
#

# A instância precisa de um Availability Domain válido na região selecionada.
data "oci_identity_availability_domains" "this" {
  compartment_id = var.compartment_id
}

# Recupera a VNIC primária criada automaticamente com a instância.
data "oci_core_vnic_attachments" "this" {
  compartment_id = var.compartment_id
  instance_id    = oci_core_instance.this.id
}

# Recupera o IP privado e o respectivo OCID da única VNIC do firewall.
# O OCID é mantido como output compatível enquanto o módulo DRG é migrado.
data "oci_core_private_ips" "primary" {
  vnic_id = local.primary_vnic_id
}
