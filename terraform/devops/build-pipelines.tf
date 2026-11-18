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

# Pipeline responsável por validar, testar e construir o user-service.
module "user_service_build_pipeline" {
  source = "./user-service"

  project_id        = oci_devops_project.ocipizza.id
  repository_id     = oci_devops_repository.ocipizza.id
  repository_url    = oci_devops_repository.ocipizza.http_url
  repository_branch = local.github_repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}

# Pipeline responsável por validar, testar e construir o order-service.
module "order_service_build_pipeline" {
  source = "./order-service"

  project_id        = oci_devops_project.ocipizza.id
  repository_id     = oci_devops_repository.ocipizza.id
  repository_url    = oci_devops_repository.ocipizza.http_url
  repository_branch = local.github_repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}

# Pipeline responsável por validar, testar e construir o notification-service.
module "notification_service_build_pipeline" {
  source = "./notification-service"

  project_id        = oci_devops_project.ocipizza.id
  repository_id     = oci_devops_repository.ocipizza.id
  repository_url    = oci_devops_repository.ocipizza.http_url
  repository_branch = local.github_repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}

# Pipeline responsável por validar, testar e construir o frontend-service.
module "frontend_service_build_pipeline" {
  source = "./frontend-service"

  project_id        = oci_devops_project.ocipizza.id
  repository_id     = oci_devops_repository.ocipizza.id
  repository_url    = oci_devops_repository.ocipizza.http_url
  repository_branch = local.github_repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}

# Pipeline responsável por validar, testar e construir o delivery-service.
module "delivery_service_build_pipeline" {
  source = "./delivery-service"

  project_id        = oci_devops_project.ocipizza.id
  repository_id     = oci_devops_repository.ocipizza.id
  repository_url    = oci_devops_repository.ocipizza.http_url
  repository_branch = local.github_repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}

# Pipeline responsável por validar, testar e construir o chatbot-service.
module "chatbot_service_build_pipeline" {
  source = "./chatbot-service"

  project_id        = oci_devops_project.ocipizza.id
  repository_id     = oci_devops_repository.ocipizza.id
  repository_url    = oci_devops_repository.ocipizza.http_url
  repository_branch = local.github_repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}

# Pipeline responsável por validar, testar e construir o admin-service.
module "admin_service_build_pipeline" {
  source = "./admin-service"

  project_id        = oci_devops_project.ocipizza.id
  repository_id     = oci_devops_repository.ocipizza.id
  repository_url    = oci_devops_repository.ocipizza.http_url
  repository_branch = local.github_repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}
