#
# vault/outputs.tf
#

output "vault_id" {
  description = "OCID do Vault persistente do OCI Pizza."
  value       = local.vault.id
}

output "key_id" {
  description = "OCID da chave usada para criptografar os Secrets."
  value       = one(data.oci_kms_keys.ocipizza.keys).id
}

output "github_pat_secret_id" {
  description = "OCID do Secret que contém o PAT do GitHub."
  value       = one(data.oci_vault_secrets.github_pat.secrets).id
}

output "ocir_credentials_secret_id" {
  description = "OCID do Secret que contém username e Auth Token do OCIR."
  value       = one(data.oci_vault_secrets.ocir_credentials.secrets).id
}
