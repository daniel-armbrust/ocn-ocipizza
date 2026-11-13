# Terraform — OCI Pizza

Este diretório contém o código Terraform responsável pela automação e pelo provisionamento da infraestrutura do OCI Pizza na Oracle Cloud Infrastructure (OCI).

## Estrutura

- `bootstrap/`: inicializa a automação OCI, incluindo IAM, OCI DevOps e OCI Resource Manager. Executado inicialmente no ambiente Linux local.
- `infrastructure/`: provisiona a infraestrutura multirregião do OCI Pizza em `sa-saopaulo-1` (GRU) e `sa-vinhedo-1` (VCP). Executado pelo OCI Resource Manager.

## Diretrizes

- Utilizar o provider oficial `oracle/oci`.
- Manter `bootstrap/` e `infrastructure/` independentes, com código, configurações e estados Terraform separados.
- Não criar módulos Terraform compartilhados entre os diretórios.
- Manter todos os recursos e configurações de cada ambiente dentro de seu respectivo diretório.
- Evitar duplicação desnecessária de código dentro de cada ambiente.
- Utilizar variáveis, referências a recursos e data sources em vez de OCIDs fixos.
- Expor via outputs os valores necessários às etapas posteriores de automação.
- Não armazenar credenciais, segredos ou arquivos Terraform State no Git.
- Manter o código declarativo, idempotente e organizado.
- Não executar `terraform apply` ou `terraform destroy` sem autorização explícita.
- Validar alterações utilizando `terraform fmt` e `terraform validate`, sempre que possível.

## Responsabilidades

O Terraform provisiona recursos OCI. A configuração interna dos clusters OKE e o deployment dos microsserviços são responsabilidades das pipelines de bootstrap Kubernetes e deployment.

Antes de implementar alterações, consultar os arquivos Terraform existentes e preservar a separação entre os dois ambientes.