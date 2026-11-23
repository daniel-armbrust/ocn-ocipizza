#
# vault/vault.tf
#

# O Vault e a chave são persistentes e ficam fora do state. O script cria ou
# recupera os recursos existentes; durante o destroy, ele não exclui nada.
resource "terraform_data" "vault" {
  input = {
    compartment_id = var.compartment_id
    region         = var.region
    script         = "${path.module}/scripts/vault.sh"
  }

  provisioner "local-exec" {
    command = "${self.input.script} apply"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
    }
  }

  provisioner "local-exec" {
    when    = destroy
    command = "${self.input.script} destroy"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
    }
  }
}

# O hash permite atualizar o Secret quando o PAT mudar sem armazenar o token
# como input do terraform_data. O conteúdo continua sendo passado ao script
# somente por variável de ambiente.
resource "terraform_data" "github_pat" {
  input = {
    compartment_id = var.compartment_id
    region         = var.region
    script         = "${path.module}/scripts/github-pat-secrets.sh"
  }

  triggers_replace = sha256(var.github_pat)

  provisioner "local-exec" {
    command = "${self.input.script} apply"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
      GITHUB_PAT     = var.github_pat
    }
  }

  provisioner "local-exec" {
    when    = destroy
    command = "${self.input.script} destroy"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
    }
  }

  depends_on = [terraform_data.vault]
}

# Armazena as credenciais do OCIR diretamente no Vault. Somente o hash usado
# para detectar rotações permanece no state do Terraform.
resource "terraform_data" "ocir_credentials" {
  input = {
    compartment_id = var.compartment_id
    region         = var.region
    script         = "${path.module}/scripts/ocir-secrets.sh"
  }

  triggers_replace = sha256("${var.ocir_username}:${var.ocir_auth_token}")

  provisioner "local-exec" {
    command = "${self.input.script} apply"

    environment = {
      COMPARTMENT_ID  = self.input.compartment_id
      OCI_REGION      = self.input.region
      OCIR_USERNAME   = var.ocir_username
      OCIR_AUTH_TOKEN = var.ocir_auth_token
    }
  }

  provisioner "local-exec" {
    when    = destroy
    command = "${self.input.script} destroy"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
    }
  }

  depends_on = [terraform_data.vault]
}

# Gera chaves de sessão e CSRF independentes por serviço e ambiente sem
# armazenar seu conteúdo no state do Terraform.
resource "terraform_data" "fastapi_secret_keys" {
  for_each = local.fastapi_secret_targets

  input = {
    compartment_id = var.compartment_id
    environment    = each.value.environment
    region         = var.region
    script         = "${path.module}/scripts/fastapi-secret-keys.sh"
    service_name   = each.value.service_name
  }

  provisioner "local-exec" {
    command = "${self.input.script} apply ${self.input.environment} ${self.input.service_name}"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
    }
  }

  provisioner "local-exec" {
    when    = destroy
    command = "${self.input.script} destroy ${self.input.environment} ${self.input.service_name}"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
    }
  }

  depends_on = [terraform_data.vault]
}

# Gera um par RSA por ambiente. O mesmo par poderá ser consumido pelos
# workloads nas duas regiões sem expor as chaves ao state do Terraform.
resource "terraform_data" "jwt_keys" {
  for_each = local.jwt_environments

  input = {
    compartment_id = var.compartment_id
    environment    = each.value
    region         = var.region
    script         = "${path.module}/scripts/jwt-keys.sh"
  }

  provisioner "local-exec" {
    command = "${self.input.script} apply ${self.input.environment}"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
    }
  }

  provisioner "local-exec" {
    when    = destroy
    command = "${self.input.script} destroy ${self.input.environment}"

    environment = {
      COMPARTMENT_ID = self.input.compartment_id
      OCI_REGION     = self.input.region
    }
  }

  depends_on = [terraform_data.vault]
}
