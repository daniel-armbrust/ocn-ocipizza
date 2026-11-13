# OCI Pizza — Terraform Bootstrap

Este diretório contém o código Terraform responsável por inicializar a plataforma de automação do projeto **OCI Pizza** na Oracle Cloud Infrastructure (OCI).

O bootstrap é executado inicialmente em um ambiente Linux local, preparando os recursos necessários para que o OCI Resource Manager provisione a infraestrutura da aplicação.

## Objetivo

Provisionar os componentes de automação necessários para gerenciar a infraestrutura e os deployments do OCI Pizza.

Os principais componentes são:

- **OCI IAM:** políticas e permissões necessárias à automação.
- **OCI DevOps:** projeto, integração com Git e pipelines de infraestrutura, bootstrap Kubernetes e deployment.
- **OCI Resource Manager:** Stack responsável por executar o Terraform localizado em `terraform/infrastructure/`.

## Estrutura

```text
bootstrap/
├── versions.tf
├── providers.tf
├── variables.tf
├── locals.tf
├── iam.tf
├── devops.tf
├── resource-manager.tf
├── outputs.tf
├── terraform.tfvars.example
└── README.md
```

## Pré-requisitos

- Terraform instalado no ambiente Linux.
- OCI CLI configurada com acesso à tenancy.
- Permissões IAM para criar e administrar os recursos de automação.
- Acesso ao repositório Git do OCI Pizza.

## Execução

A partir da raiz do repositório:

```bash
cd terraform/bootstrap
```

Inicializar o Terraform:

```bash
terraform init
```

Validar a configuração:

```bash
terraform fmt -check
terraform validate
```

Visualizar as alterações:

```bash
terraform plan
```

Provisionar os recursos:

```bash
terraform apply
```

A execução inicial ocorre localmente. Execuções posteriores podem ser realizadas para atualizar os recursos de automação.

## Fluxo de provisionamento

```text
Linux Local
 |
 | terraform apply
 v
Terraform Bootstrap
 |
 +-- OCI IAM
 |
 +-- OCI DevOps
 |    +-- Infrastructure Pipeline
 |    +-- Kubernetes Bootstrap Pipeline
 |    +-- Application Deployment Pipeline
 |
 +-- OCI Resource Manager
      |
      +-- Stack: ocipizza-infrastructure
           |
           +-- terraform/infrastructure/
                |
                +-- sa-saopaulo-1 (GRU)
                +-- sa-vinhedo-1 (VCP)
```

## Gerenciamento do Terraform State

O bootstrap possui um Terraform State independente do projeto `terraform/infrastructure/`.

O estado deve ser armazenado de maneira persistente e protegida, preferencialmente em um backend remoto com controle de acesso.

Não versionar arquivos `terraform.tfstate`, arquivos de credenciais ou valores sensíveis no repositório Git.

## Responsabilidades

Este diretório é responsável exclusivamente pela plataforma de automação OCI.

O provisionamento de VCNs, clusters OKE, Load Balancers, bancos de dados e demais recursos da aplicação pertence a `terraform/infrastructure/`.

A configuração interna do Kubernetes é realizada pela pipeline de bootstrap Kubernetes, após o provisionamento dos clusters OKE.