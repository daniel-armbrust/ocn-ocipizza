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

output "mysql_credentials" {
  description = "Credenciais administrativas e de replicação do MySQL armazenadas no OCI Vault."
  value = {
    admin_username       = data.external.database_credentials.result.admin_username
    admin_password       = data.external.database_credentials.result.admin_password
    replication_username = data.external.database_credentials.result.replication_username
    replication_password = data.external.database_credentials.result.replication_password
  }
  sensitive = true
}

output "mysql_admin_credentials_secret_id" {
  description = "OCID do Secret com as credenciais administrativas do MySQL."
  value       = one(data.oci_vault_secrets.mysql_admin_credentials.secrets).id
}

output "mysql_replication_credentials_secret_id" {
  description = "OCID do Secret com as credenciais do usuário de replicação do MySQL."
  value       = one(data.oci_vault_secrets.mysql_replication_credentials.secrets).id
}

output "user_service_database_credentials_secret_id" {
  description = "OCID do Secret com as credenciais de banco do user-service."
  value       = one(data.oci_vault_secrets.user_service_database_credentials.secrets).id
}
