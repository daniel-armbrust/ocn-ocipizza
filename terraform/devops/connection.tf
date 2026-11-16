#
# devops/connection.tf
#

# Conexão autenticada que será usada pelas pipelines para acessar o repositório
# oficial do OCI Pizza no GitHub.
resource "oci_devops_connection" "github_ocipizza" {
  project_id      = oci_devops_project.ocipizza.id
  connection_type = "GITHUB_ACCESS_TOKEN"
  display_name    = local.github_connection_name
  description     = "Conexão com ${local.github_repository_url}."
  access_token    = var.github_pat_secret_id
}
