#
# devops/bootstrap/build-pipeline.tf
#

# Orquestra os bootstraps dos serviços da aplicação. Cada serviço deve possuir
# seu próprio Managed Build stage para manter configuração, logs e falhas
# isolados. Por enquanto, somente o pizza-service participa do fluxo.
resource "oci_devops_build_pipeline" "bootstrap_ocipizza" {
  project_id   = var.project_id
  display_name = local.build_pipeline_name
  description  = "Pipeline de inicialização dos dados dos serviços da aplicação OCI Pizza."

  build_pipeline_parameters {
    items {
      name          = "NOSQL_COMPARTMENT_ID"
      default_value = var.compartment_id
      description   = "OCID do compartment que contém a tabela OCI NoSQL do pizza-service."
    }
  }
}

# Managed Build responsável pelo bootstrap do pizza-service.
module "pizza_service" {
  source = "./pizza-service"

  build_pipeline_id = oci_devops_build_pipeline.bootstrap_ocipizza.id
  repository_id     = var.repository_id
  repository_url    = var.repository_url
  repository_branch = var.repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}
