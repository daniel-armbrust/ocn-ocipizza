#
# devops/build-pipelines.tf
#

# Pipeline responsável por validar, testar e construir o pizza-service.
module "pizza_service_build_pipeline" {
  source = "./pizza-service"

  project_id        = oci_devops_project.ocipizza.id
  repository_id     = oci_devops_repository.ocipizza.id
  repository_url    = oci_devops_repository.ocipizza.http_url
  repository_branch = local.github_repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}
