#
# vault/vault.tf
#

# O Vault e a chave são persistentes e ficam fora do state. O script cria ou
# recupera os recursos existentes; durante o destroy, ele não exclui nada.
resource "terraform_data" "vault" {
  input = {
    compartment_id = var.compartment_id
    region         = var.region
    script         = "${path.module}/scripts/create-vault.sh"
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
    script         = "${path.module}/scripts/create-secret.sh"
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
