#
# devops/repository.tf
#

# Espelha o repositório oficial do OCI Pizza no OCI Code Repository. A
# external connection fornece o PAT necessário para autenticar no GitHub.
resource "oci_devops_repository" "ocipizza" {
  project_id      = oci_devops_project.ocipizza.id
  name            = local.github_repository_name
  description     = "Mirror do repositório oficial do OCI Pizza no GitHub."
  repository_type = "MIRRORED"
  default_branch  = local.github_repository_branch

  mirror_repository_config {
    connector_id   = oci_devops_connection.github_ocipizza.id
    repository_url = local.github_repository_url

    # A sincronização padrão verifica atualizações no GitHub a cada 30 minutos.
    trigger_schedule {
      schedule_type = "DEFAULT"
    }
  }
}
