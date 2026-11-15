#
# resource-manager.tf
#

resource "terraform_data" "configuration_source_provider" {
  input = {
    compartment_id      = var.resource_manager_compartment_id
    destroy_script_path = "${path.module}/scripts/resource-manager-source-provider-destroy.sh"
  }

  triggers_replace = {
    compartment_id       = var.resource_manager_compartment_id
    source_script_sha256 = filesha256("${path.module}/scripts/resource-manager-source-provider.sh")
  }

  # Executa a OCI CLI para criar ou atualizar o Configuration Source Provider
  # que conecta o OCI Resource Manager ao repositório da OCI Pizza no GitHub.
  provisioner "local-exec" {
    command     = "${path.module}/scripts/resource-manager-source-provider.sh"
    interpreter = ["/usr/bin/env", "bash"]

    environment = {
      RESOURCE_MANAGER_COMPARTMENT_ID = var.resource_manager_compartment_id
    }
  }

  # Remove da OCI o Configuration Source Provider criado pelo local-exec.
  provisioner "local-exec" {
    when        = destroy
    command     = self.input.destroy_script_path
    interpreter = ["/usr/bin/env", "bash"]

    environment = {
      RESOURCE_MANAGER_COMPARTMENT_ID = self.input.compartment_id
    }
  }
}

resource "terraform_data" "resource_manager_stack" {
  depends_on = [
    oci_identity_policy.ocipizza_instance_principals,
    oci_identity_policy.ocipizza_infrastructure_deployer,
    oci_identity_policy.ocipizza_service_principals,
    terraform_data.configuration_source_provider,
  ]

  input = {
    compartment_id      = var.resource_manager_compartment_id
    destroy_script_path = "${path.module}/scripts/resource-manager-stack-destroy.sh"
    stack_name          = var.resource_manager_stack_name
  }

  triggers_replace = {
    stack_compartment_id          = var.resource_manager_compartment_id
    stack_name                    = var.resource_manager_stack_name
    stack_script_sha256           = filesha256("${path.module}/scripts/resource-manager-config.sh")
    repository_url                = var.resource_manager_repository_url
    repository_branch             = var.resource_manager_repository_branch
    working_directory             = var.resource_manager_working_directory
    terraform_version             = var.resource_manager_terraform_version
    infrastructure_compartment_id = var.infrastructure_compartment_id
    firewall_ssh_public_key       = var.firewall_ssh_public_key
    oke_worker_ssh_public_key     = var.oke_worker_ssh_public_key
  }

  # Executa a OCI CLI para criar ou atualizar a stack que utiliza o código de
  # terraform/infrastructure e recebe as entradas necessárias ao provisionamento.
  provisioner "local-exec" {
    command     = "${path.module}/scripts/resource-manager-config.sh"
    interpreter = ["/usr/bin/env", "bash"]

    environment = {
      RESOURCE_MANAGER_COMPARTMENT_ID    = var.resource_manager_compartment_id
      RESOURCE_MANAGER_STACK_NAME        = var.resource_manager_stack_name
      RESOURCE_MANAGER_REPOSITORY_URL    = var.resource_manager_repository_url
      RESOURCE_MANAGER_REPOSITORY_BRANCH = var.resource_manager_repository_branch
      RESOURCE_MANAGER_WORKING_DIRECTORY = var.resource_manager_working_directory
      RESOURCE_MANAGER_TERRAFORM_VERSION = var.resource_manager_terraform_version
      INFRASTRUCTURE_COMPARTMENT_ID      = var.infrastructure_compartment_id
      FIREWALL_SSH_PUBLIC_KEY            = var.firewall_ssh_public_key
      OKE_WORKER_SSH_PUBLIC_KEY          = var.oke_worker_ssh_public_key
    }
  }

  # Remove a stack antes que o Source Provider associado seja excluído.
  provisioner "local-exec" {
    when        = destroy
    command     = self.input.destroy_script_path
    interpreter = ["/usr/bin/env", "bash"]

    environment = {
      RESOURCE_MANAGER_COMPARTMENT_ID = self.input.compartment_id
      RESOURCE_MANAGER_STACK_NAME     = self.input.stack_name
    }
  }
}
