#
# vault/datasource.tf
#

# As consultas abaixo recuperam somente os OCIDs necessários aos demais
# módulos. Vault, chave e Secret não são administrados como resources.
data "oci_kms_vaults" "ocipizza" {
  compartment_id = var.compartment_id

  depends_on = [terraform_data.vault]
}

data "oci_kms_keys" "ocipizza" {
  compartment_id      = var.compartment_id
  management_endpoint = local.vault.management_endpoint

  filter {
    name   = "display_name"
    values = [local.key_name]
  }

  filter {
    name   = "state"
    values = ["ENABLED"]
  }

  depends_on = [terraform_data.vault]
}

data "oci_vault_secrets" "github_pat" {
  compartment_id = var.compartment_id
  name           = local.secret_name
  state          = "ACTIVE"
  vault_id       = local.vault.id

  depends_on = [terraform_data.github_pat]
}
