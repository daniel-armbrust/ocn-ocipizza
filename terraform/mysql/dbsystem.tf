#
# mysql/dbsystem.tf
#

resource "oci_mysql_mysql_db_system" "this" {
  compartment_id      = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.this.availability_domains[0].name
  subnet_id           = var.subnet_id
  configuration_id    = oci_mysql_mysql_configuration.this.id
  shape_name          = "MySQL.2"
  display_name        = local.display_name
  description         = local.is_primary ? "MySQL primary da OCI Pizza em GRU." : "MySQL secondary read-only da OCI Pizza em VCP."

  admin_username = var.admin_username
  admin_password = var.admin_password
  database_mode  = local.is_primary ? "READ_WRITE" : "READ_ONLY"

  data_storage_size_in_gb = 50

  data_storage {
    is_auto_expand_storage_enabled = true
    max_storage_size_in_gbs        = 500
  }

  backup_policy {
    is_enabled        = true
    retention_in_days = 7
    window_start_time = "03:00"

    pitr_policy {
      is_enabled = true
    }

    dynamic "copy_policies" {
      for_each = local.is_primary ? [1] : []

      content {
        copy_to_region                = "sa-vinhedo-1"
        backup_copy_retention_in_days = 7
      }
    }
  }

  deletion_policy {
    automatic_backup_retention = "DELETE"
    final_backup               = "SKIP_FINAL_BACKUP"
    is_delete_protected        = false
  }

  maintenance {
    maintenance_schedule_type = "REGULAR"
    version_preference        = "OLDEST"
    version_track_preference  = "LONG_TERM_SUPPORT"
    window_start_time         = "SUNDAY 04:00"
  }

  secure_connections {
    certificate_generation_type = "SYSTEM"
  }

  state = "ACTIVE"

  timeouts {
    create = "2h"
    update = "2h"
    delete = "2h"
  }
}
