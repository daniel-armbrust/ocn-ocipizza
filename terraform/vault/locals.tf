#
# vault/locals.tf
#

locals {
  vault_name                        = "ocipizza-vault"
  key_name                          = "ocipizza-vault-key"
  secret_name                       = "ocipizza-github-pat"
  ocir_credentials_secret_name      = "ocipizza-ocir-credentials"
  mysql_admin_secret_name           = "ocipizza-mysql-admin-credentials"
  mysql_replication_secret_name     = "ocipizza-mysql-replication-credentials"
  user_service_database_secret_name = "ocipizza-user-service-database-credentials"

  fastapi_secret_targets = {
    "admin-service-homol" = {
      environment  = "homol"
      service_name = "admin-service"
    }
    "admin-service-prod" = {
      environment  = "prod"
      service_name = "admin-service"
    }
    "frontend-service-homol" = {
      environment  = "homol"
      service_name = "frontend-service"
    }
    "frontend-service-prod" = {
      environment  = "prod"
      service_name = "frontend-service"
    }
  }

  jwt_environments = toset(["homol", "prod"])

  active_vaults = [
    for vault in data.oci_kms_vaults.ocipizza.vaults : vault
    if vault.display_name == local.vault_name && vault.state == "ACTIVE"
  ]

  vault = one(local.active_vaults)
}
