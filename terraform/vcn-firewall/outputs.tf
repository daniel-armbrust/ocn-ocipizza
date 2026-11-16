#
# vcn-firewall/outputs.tf
#

output "vcn_id" {
  value = oci_core_vcn.this.id
}

output "subnet_ids" {
  value = merge(
    { for key, subnet in oci_core_subnet.this : key => subnet.id },
    {
      # Aliases temporários preservam o contrato atual do compute-firewall.
      # Eles serão removidos quando o módulo do firewall for ajustado para a
      # nova topologia de uma única sub-rede de VNICs.
      mgmt    = oci_core_subnet.this["firewall"].id
      trust   = oci_core_subnet.this["firewall"].id
      untrust = oci_core_subnet.this["firewall"].id
    }
  )
}

output "gateway_ids" {
  value = {
    nat     = oci_core_nat_gateway.this.id
    service = oci_core_service_gateway.this.id
  }
}
