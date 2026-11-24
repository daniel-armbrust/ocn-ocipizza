#
# mysql/locals.tf
#

locals {
  is_primary = var.region_key == "gru"

  display_name       = "mysql-${var.region_key}"
  configuration_name = "mysql-replication-${var.region_key}"

  # O clone cross-region exige que os binlogs da origem permaneçam disponíveis
  # por pelo menos 96 horas (345600 segundos).
  binlog_expire_logs_seconds = 345600
}
