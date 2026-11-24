#
# devops/bootstrap/build-pipeline.tf
#

# Orquestra os bootstraps dos serviços da aplicação. Cada serviço deve possuir
# seu próprio Managed Build stage para manter configuração, logs e falhas
# isolados. O MySQL prepara a replicação e o pizza-service inicializa seu
# próprio conjunto de dados.
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

    items {
      name          = "COMPARTMENT_ID"
      default_value = var.compartment_id
      description   = "OCID do compartment que contém os DB Systems MySQL."
    }

    items {
      name          = "MYSQL_PRIMARY_REGION"
      default_value = var.mysql_primary_region
      description   = "Região do MySQL primary."
    }

    items {
      name          = "MYSQL_SECONDARY_REGION"
      default_value = var.mysql_secondary_region
      description   = "Região do MySQL secondary."
    }

    items {
      name          = "MYSQL_PRIMARY_HOST"
      default_value = var.mysql_primary_host
      description   = "Nome DNS privado do MySQL primary."
    }

    items {
      name          = "MYSQL_PRIMARY_DB_SYSTEM_ID"
      default_value = var.mysql_primary_db_system_id
      description   = "OCID do MySQL DB System primary."
    }

    items {
      name          = "MYSQL_SECONDARY_DB_SYSTEM_ID"
      default_value = var.mysql_secondary_db_system_id
      description   = "OCID do MySQL DB System secondary."
    }

    items {
      name          = "MYSQL_ADMIN_CREDENTIALS_SECRET_ID"
      default_value = var.mysql_admin_credentials_secret_id
      description   = "OCID do Secret com as credenciais administrativas do MySQL."
    }

    items {
      name          = "MYSQL_REPLICATION_CREDENTIALS_SECRET_ID"
      default_value = var.mysql_replication_credentials_secret_id
      description   = "OCID do Secret com as credenciais de replicação do MySQL."
    }

    items {
      name          = "DATABASE_CREDENTIALS_SECRET_ID"
      default_value = var.user_service_database_credentials_secret_id
      description   = "OCID do Secret com as credenciais de banco do user-service."
    }
  }
}

# Managed Build responsável por preparar a replicação regional do MySQL.
module "mysql" {
  source = "./mysql"

  build_pipeline_id = oci_devops_build_pipeline.bootstrap_ocipizza.id
  repository_id     = var.repository_id
  repository_url    = var.repository_url
  repository_branch = var.repository_branch
  private_subnet_id = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
}

# Managed Build responsável por preparar o banco do user-service. O stage só é
# iniciado depois que o bootstrap da replicação do MySQL termina com sucesso.
module "user_service" {
  source = "./user-service"

  build_pipeline_id    = oci_devops_build_pipeline.bootstrap_ocipizza.id
  predecessor_stage_id = module.mysql.build_stage_id
  repository_id        = var.repository_id
  repository_url       = var.repository_url
  repository_branch    = var.repository_branch
  private_subnet_id    = var.private_subnet_id

  build_runner_image         = "OL8_X86_64_STANDARD_10"
  build_runner_ocpus         = 2
  build_runner_memory_in_gbs = 4
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
