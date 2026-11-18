#
# devops/order-service/build-pipeline.tf
#

resource "oci_devops_build_pipeline" "order_service" {
  project_id   = var.project_id
  display_name = local.build_pipeline_name
  description  = "Pipeline de validação, testes e construção da imagem do order-service."
}

resource "oci_devops_build_pipeline_stage" "build_order_service" {
  build_pipeline_id         = oci_devops_build_pipeline.order_service.id
  build_pipeline_stage_type = "BUILD"
  display_name              = "build-order-service"
  description               = "Valida, testa e constrói a imagem de container do order-service."

  build_pipeline_stage_predecessor_collection {
    items {
      id = oci_devops_build_pipeline.order_service.id
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

# Publica no OCIR a imagem produzida pelo Managed Build.
resource "oci_devops_build_pipeline_stage" "deliver_order_service_image" {
  build_pipeline_id         = oci_devops_build_pipeline.order_service.id
  build_pipeline_stage_type = "DELIVER_ARTIFACT"
  display_name              = "deliver-order-service-image"
  description               = "Publica no OCIR a imagem construída para o order-service."

  build_pipeline_stage_predecessor_collection {
    items {
      id = oci_devops_build_pipeline_stage.build_order_service.id
    }
  }

  deliver_artifact_collection {
    items {
      artifact_id   = oci_devops_deploy_artifact.order_service_image.id
      artifact_name = local.output_artifact_name
    }
  }
}
