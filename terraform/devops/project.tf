#
# devops/project.tf
#

resource "oci_devops_project" "ocipizza" {
  compartment_id = var.compartment_id
  name           = local.project_name
  description    = "Projeto OCI DevOps responsável pelo CI/CD do OCI Pizza."

  notification_config {
    topic_id = var.notification_topic_id
  }
}
