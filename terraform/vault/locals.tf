#
# vault/locals.tf
#

locals {
  vault_name  = "ocipizza-vault"
  key_name    = "ocipizza-vault-key"
  secret_name = "ocipizza-github-pat"

  active_vaults = [
    for vault in data.oci_kms_vaults.ocipizza.vaults : vault
    if vault.display_name == local.vault_name && vault.state == "ACTIVE"
  ]
  vault = one(local.active_vaults)
}
