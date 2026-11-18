#
# devops/frontend-service/build-pipeline.tf
#

resource "oci_devops_build_pipeline" "frontend_service" {
  project_id   = var.project_id
  display_name = local.build_pipeline_name
  description  = "Pipeline de validação, testes e construção da imagem do frontend-service."
}

resource "oci_devops_build_pipeline_stage" "build_frontend_service" {
  build_pipeline_id         = oci_devops_build_pipeline.frontend_service.id
  build_pipeline_stage_type = "BUILD"
  display_name              = "build-frontend-service"
  description               = "Valida, testa e constrói a imagem de container do frontend-service."

  build_pipeline_stage_predecessor_collection {
    items {
      id = oci_devops_build_pipeline.frontend_service.id
    }
  }

  build_source_collection {
    items {
      branch          = var.repository_branch
      connection_type = "DEVOPS_CODE_REPOSITORY"
      name            = local.build_source_name
      repository_id   = var.repository_id
      repository_url  = var.repository_url
    }
  }

  primary_build_source = local.build_source_name
  build_spec_file      = local.build_spec_file
  image                = var.build_runner_image

  build_runner_shape_config {
    build_runner_type = "CUSTOM"
    ocpus             = var.build_runner_ocpus
    memory_in_gbs     = var.build_runner_memory_in_gbs
  }

  private_access_config {
    network_channel_type = "SERVICE_VNIC_CHANNEL"
    subnet_id            = var.private_subnet_id
  }

  stage_execution_timeout_in_seconds = 900
}
