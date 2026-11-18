# OCI Pizza — Terraform

Este diretório é o único root module Terraform do OCI Pizza. Ele provisiona a
infraestrutura multi-região, o IAM, os serviços gerenciados e os recursos de
OCI DevOps. O projeto não utiliza OCI Resource Manager.

## Arquitetura

A infraestrutura utiliza as regiões de São Paulo (`sa-saopaulo-1`) e Vinhedo
(`sa-vinhedo-1`). Os providers regionais são configurados em `providers.tf` e
repassados explicitamente aos módulos locais.

Os principais componentes são:

- VCNs de firewall, OKE, banco de dados e serviços;
- DRGs, Remote Peering e inspeção de tráfego pelos Compute Firewalls;
- clusters OKE em São Paulo e Vinhedo;
- OCI Cache com Redis 7, NoSQL, Object Storage e Queue;
- DNS, Logging, Network Load Balancers e IPs públicos reservados;
- repositório privado de imagens do `pizza-service` no OCIR;
- IAM dos workloads, do OCI DevOps e dos serviços gerenciados;
- OCI Notifications, projeto OCI DevOps e conexão externa com o GitHub.

O módulo `email-delivery/` permanece no repositório, mas suas instanciações em
`gru.tf` e `vcp.tf` estão comentadas. Nenhum domínio, remetente ou DKIM do Email
Delivery é criado enquanto essa integração estiver desativada.

A VCN-SERVICES de cada região possui duas subnets: uma pública para Load
Balancers e outra privada para serviços. Cada subnet utiliza sua própria
Security List e sua própria Route Table. A Security List da subnet privada
permite ingresso e egresso IPv4 para todos os protocolos; nenhum NSG é usado
para o OCI Cache.

O OCI Cache cria automaticamente a Security List `redis-security-list` fora
do controle do Terraform. Para evitar inconsistências no state, o módulo
executa `oci-cache/scripts/delete-seclist.sh` após a criação do cluster. O
script remove essa associação da subnet do cluster e exclui somente a Security
List com esse nome na VCN regional. Essa automação é um workaround temporário
e deve ser reavaliada quando o serviço deixar de criar a Security List
adicional.

Nos Network Load Balancers de inspeção, o `firewall-1` é o backend primário e
o `firewall-2` permanece como backup. O segundo firewall somente recebe tráfego
quando o primário não está apto a atendê-lo.

## Pré-requisitos

- Terraform 1.5 ou superior;
- credenciais da OCI configuradas no ambiente local;
- permissão para administrar os recursos no compartment da aplicação;
- permissão para criar dynamic groups e policies no root compartment da
  tenancy.

O usuário ou principal que executa o Terraform já deve possuir essas
permissões. Este código não cria uma policy para autorizar seu próprio executor.

### Autenticação na OCI

Por padrão, o provider utiliza a autenticação por API Key definida no profile
`DEFAULT` do arquivo `$HOME/.oci/config`. Esse profile deve conter o OCID da
tenancy, o OCID do usuário, o fingerprint e o caminho da chave privada de API.

Para usar outro profile do mesmo arquivo, exporte antes da execução:

```bash
export OCI_CONFIG_FILE_PROFILE="NOME_DO_PROFILE"
```

Essa variável configura a autenticação do provider e não utiliza o prefixo
`TF_VAR_`.

## Variáveis de ambiente

O Terraform recebe variáveis de ambiente com o prefixo `TF_VAR_`.

| Variável | Obrigatória | Padrão | Finalidade |
| --- | --- | --- | --- |
| `TF_VAR_compartment_id` | Sim | — | Compartment que receberá os recursos do OCI Pizza. |
| `TF_VAR_tenancy_id` | Sim | — | Tenancy usada como root compartment das policies e dos dynamic groups. |
| `TF_VAR_firewall_ssh_public_key` | Sim | — | Conteúdo da chave pública dos Compute Firewalls. |
| `TF_VAR_oke_worker_ssh_public_key` | Sim | — | Conteúdo da chave pública dos worker nodes do OKE. |
| `TF_VAR_notification_email` | Sim | — | E-mail inscrito no Topic usado pelo OCI DevOps. |
| `TF_VAR_github_pat` | Sim | — | PAT armazenado como Secret no OCI Vault para acesso do OCI DevOps ao GitHub. |
| `TF_VAR_iam_dynamic_group_name` | Não | `ocipizza-instances` | Nome do dynamic group dos workloads. |
| `TF_VAR_iam_policy_name` | Não | `ocipizza-instance-principals` | Nome da policy dos workloads. |
| `TF_VAR_devops_dynamic_group_name` | Não | `ocipizza-devops` | Nome do dynamic group do OCI DevOps. |
| `TF_VAR_devops_policy_name` | Não | `ocipizza-devops` | Nome da policy do OCI DevOps. |
| `TF_VAR_service_principals_policy_name` | Não | `ocipizza-service-principals` | Nome da policy dos serviços gerenciados. |

Exemplo:

```bash
export TF_VAR_compartment_id="ocid1.compartment.oc1..substitua"
export TF_VAR_tenancy_id="ocid1.tenancy.oc1..substitua"
export TF_VAR_firewall_ssh_public_key="$(cat $HOME/ocn-ocipizza/terraform/ssh-keys/firewall.pub)"
export TF_VAR_oke_worker_ssh_public_key="$(cat $HOME/ocn-ocipizza/terraform/ssh-keys/worker-nodes.pub)"
export TF_VAR_notification_email="seu-email@exemplo.com"
export TF_VAR_github_pat="github_pat_substitua"
```

As variáveis de chaves recebem somente o conteúdo das chaves públicas. Nunca
adicione chaves privadas, tokens ou outros segredos ao repositório.

`TF_VAR_github_pat` é sensível e não aparece nos outputs. O Terraform armazena
somente seu hash no state para detectar mudanças; o conteúdo é enviado ao
script do Vault por variável de ambiente e armazenado diretamente no Secret.

## IAM

O arquivo `iam.tf` cria somente as identidades e policies consumidas pelos
recursos do OCI Pizza:

- `ocipizza-instances`: reúne Compute Instances e Container Instances do
  compartment da aplicação e permite aos workloads consumir NoSQL, Object
  Storage, Queue, Secrets, Logging e OCIR;
- `ocipizza-devops`: reúne os resource principals de build pipelines,
  deployment pipelines, repositórios e conexões do OCI DevOps, permitindo
  construir, publicar e implantar os artefatos;
- `ocipizza-service-principals`: permite ao OKE administrar IPs privados e ao
  Object Storage realizar a replicação entre São Paulo e Vinhedo.

As policies e os dynamic groups são criados no root compartment da tenancy,
mas as permissões sobre os recursos permanecem limitadas ao compartment
informado em `TF_VAR_compartment_id`.

## OCI Notifications

O módulo `notifications/` cria em São Paulo o Topic
`ocipizza-devops-notifications` e sua assinatura de e-mail. Depois do apply, a
OCI envia uma mensagem ao endereço definido em `TF_VAR_notification_email`.
A assinatura permanece `PENDING` e não recebe notificações até que o
destinatário confirme o link enviado.

O output `notifications_topic_id` fornece o OCID que será referenciado pelo
projeto OCI DevOps.

## Vault e PAT do GitHub

O módulo `vault/` chama scripts idempotentes para criar em São Paulo o Vault
`ocipizza-vault`, uma chave AES de 256 bits protegida por HSM e o Secret
`ocipizza-github-pat`. Esses recursos são criados pela OCI CLI e ficam fora do
state do Terraform. O Secret recebe o PAT informado por `TF_VAR_github_pat` e
é referenciado pela conexão do OCI DevOps com o GitHub.

Quando os recursos já existem, os scripts os reutilizam. Se o PAT mudar, uma
nova versão do Secret é criada somente quando o conteúdo for diferente. No
`terraform destroy`, os scripts são chamados em modo de destruição, mas não
excluem o Vault, a chave nem o Secret. Assim, esses recursos persistentes podem
ser usados novamente por um próximo `terraform apply`.

Esse fluxo requer OCI CLI, `jq` e `base64` instalados na máquina que executa o
Terraform. A autenticação usada pelos scripts é a mesma configuração local da
OCI descrita na seção de autenticação.

## Projeto OCI DevOps

O módulo `devops/` cria em São Paulo o projeto `ocipizza`. O projeto referencia
o Topic `ocipizza-devops-notifications` para publicar seus eventos.

O Service Log `log-ocipizza-devops` é habilitado no `loggroup-ocipizza` de São
Paulo, com categoria `all` e retenção de 30 dias. Ele reúne os logs de build e
deployment do projeto e permite executar e acompanhar Manual Runs das
pipelines no OCI DevOps.

O módulo também cria a conexão externa `github-ocipizza`, do tipo
`GITHUB_ACCESS_TOKEN`. A conexão referencia o Secret `ocipizza-github-pat` no
Vault e autentica o acesso ao repositório:

```text
https://github.com/daniel-armbrust/ocn-ocipizza.git
```

A partir dessa conexão, o OCI DevOps cria o Code Repository `ocn-ocipizza` do
tipo `MIRRORED`. Na criação, o conteúdo da branch `master` é importado do GitHub.
Depois disso, a sincronização padrão do serviço verifica novas alterações a
cada 30 minutos. As Build Pipelines poderão consumir esse mirror pelo OCID
publicado no output `devops_mirrored_repository_id`.

## OCI Container Registry

O módulo `ocir/` cria em São Paulo o repositório privado
`ocipizza/pizza-service`. As imagens publicadas utilizam tags baseadas no
identificador da execução do build para distinguir cada versão produzida. A
configuração de imutabilidade não é declarada porque a API do OCI Container
Registry ainda não permite definir `is_immutable` na criação do repositório.

O namespace único da tenancy é consultado uma vez no root module, em
`datasource.tf`, e repassado aos módulos `objectstorage/` e `devops/`. Esse
valor é usado tanto pelos buckets e sua replicação quanto para compor a URL do
repositório OCIR consumida pela build pipeline.

Os outputs `ocir_pizza_service_repository_id`,
`ocir_pizza_service_repository_namespace` e
`ocir_pizza_service_repository_url` fornecem os valores necessários para a
futura configuração do deployment artifact e do stage `DELIVER_ARTIFACT`.

### Build pipeline do pizza-service

O submódulo `devops/pizza-service/` cria a build pipeline `pizza-service` e um
Managed Build stage baseado em Oracle Linux 8, com 2 OCPUs e 4 GB de memória.
Esses valores são definidos na instanciação do módulo
`pizza_service_build_pipeline`, em `devops/build-pipelines.tf`. O stage lê
`services/pizza-service/build_spec.yaml` da branch `master` do Code Repository
espelhado, valida o código Python, executa os testes e audita as dependências
com `pip-audit` em ambientes virtuais isolados. Depois, constrói com Podman a
imagem identificada pelo hash completo do commit.

O Managed Build utiliza Private Access pela subnet privada `services` da
VCN-SERVICES de São Paulo. Todo o tráfego de saída do runner segue as rotas da
VCN, inclusive os acessos ao PyPI e aos registries usados durante a construção
da imagem. O `podman build` utiliza a rede do host para preservar essa
conectividade dentro do runner privado.

A imagem declarada como output do build é entregue pelo stage
`deliver-pizza-service-image` ao repositório privado
`ocipizza/pizza-service` no OCIR. A tag utiliza o identificador da execução por
meio da variável `BUILDRUN_HASH`, exportada pelo Build Spec com o hash completo
do commit, preservando a rastreabilidade da imagem publicada para o código que
a produziu. Triggers e integração com a deployment pipeline serão adicionados
separadamente.

### Build pipeline do user-service

O submódulo `devops/user-service/` cria a build pipeline `user-service` e o
Managed Build stage `build-user-service`. O runner utiliza Oracle Linux 8, 2
OCPUs, 4 GB de memória e Private Access pela subnet privada `services` da
VCN-SERVICES de São Paulo.

O stage lê `services/user-service/build_spec.yaml` da branch `master`, valida o
código Python, executa os testes, audita as dependências e constrói com Podman
a imagem `ocipizza/user-service`, identificada pelo hash completo do commit. O
stage `deliver-user-service-image` entrega esse output ao repositório privado
`ocipizza/user-service` no OCIR, usando como tag o hash completo do commit
exportado pelo Build Spec na variável `BUILDRUN_HASH`.

### Build pipeline do order-service

O submódulo `devops/order-service/` cria a build pipeline `order-service` e o
Managed Build stage `build-order-service`. O runner utiliza Oracle Linux 8, 2
OCPUs, 4 GB de memória e Private Access pela subnet privada `services` da
VCN-SERVICES de São Paulo.

O stage lê `services/order-service/build_spec.yaml` da branch `master`, valida
o código Python, executa os testes, audita as dependências e constrói com
Podman a imagem `ocipizza/order-service`, identificada pelo hash completo do
commit. O stage `deliver-order-service-image` entrega esse output ao repositório
privado `ocipizza/order-service` no OCIR, usando como tag o hash completo do
commit exportado pelo Build Spec na variável `BUILDRUN_HASH`.

### Build pipeline do notification-service

O submódulo `devops/notification-service/` cria a build pipeline
`notification-service` e o Managed Build stage `build-notification-service`. O
runner utiliza Oracle Linux 8, 2 OCPUs, 4 GB de memória e Private Access pela
subnet privada `services` da VCN-SERVICES de São Paulo.

O stage lê `services/notification-service/build_spec.yaml` da branch `master`,
valida o código Python, executa os testes, audita as dependências e constrói
com Podman a imagem `ocipizza/notification-service`, identificada pelo hash
completo do commit. O stage `deliver-notification-service-image` entrega esse
output ao repositório privado `ocipizza/notification-service` no OCIR, usando
como tag o hash completo do commit exportado pelo Build Spec na variável
`BUILDRUN_HASH`.

### Build pipeline do frontend-service

O submódulo `devops/frontend-service/` cria a build pipeline
`frontend-service` e o Managed Build stage `build-frontend-service`. O runner
utiliza Oracle Linux 8, 2 OCPUs, 4 GB de memória e Private Access pela subnet
privada `services` da VCN-SERVICES de São Paulo.

O stage lê `services/frontend-service/build_spec.yaml` da branch `master`,
valida o código Python, executa os testes, audita as dependências e constrói
com Podman a imagem `ocipizza/frontend-service`, identificada pelo hash
completo do commit. O stage `deliver-frontend-service-image` entrega esse
output ao repositório privado `ocipizza/frontend-service` no OCIR, usando como
tag o hash completo do commit exportado pelo Build Spec na variável
`BUILDRUN_HASH`.

### Build pipeline do delivery-service

O submódulo `devops/delivery-service/` cria a build pipeline
`delivery-service` e o Managed Build stage `build-delivery-service`. O runner
utiliza Oracle Linux 8, 2 OCPUs, 4 GB de memória e Private Access pela subnet
privada `services` da VCN-SERVICES de São Paulo.

O stage lê `services/delivery-service/build_spec.yaml` da branch `master`,
valida o código Python, executa os testes, audita as dependências e constrói
com Podman a imagem `ocipizza/delivery-service`, identificada pelo hash
completo do commit. O stage `deliver-delivery-service-image` entrega esse
output ao repositório privado `ocipizza/delivery-service` no OCIR, usando como
tag o hash completo do commit exportado pelo Build Spec na variável
`BUILDRUN_HASH`.

### Build pipeline do chatbot-service

O submódulo `devops/chatbot-service/` cria a build pipeline `chatbot-service`
e o Managed Build stage `build-chatbot-service`. O runner utiliza Oracle Linux
8, 2 OCPUs, 4 GB de memória e Private Access pela subnet privada `services` da
VCN-SERVICES de São Paulo.

O stage lê `services/chatbot-service/build_spec.yaml` da branch `master`,
valida o código Python, executa os testes, audita as dependências e constrói
com Podman a imagem `ocipizza/chatbot-service`, identificada pelo hash completo
do commit. O stage `deliver-chatbot-service-image` entrega esse output ao
repositório privado `ocipizza/chatbot-service` no OCIR, usando como tag o hash
completo do commit exportado pelo Build Spec na variável `BUILDRUN_HASH`.

### Build pipeline do admin-service

O submódulo `devops/admin-service/` cria a build pipeline `admin-service` e o
Managed Build stage `build-admin-service`. O runner utiliza Oracle Linux 8, 2
OCPUs, 4 GB de memória e Private Access pela subnet privada `services` da
VCN-SERVICES de São Paulo.

O stage lê `services/admin-service/build_spec.yaml` da branch `master`, valida
o código Python, executa os testes, audita as dependências e constrói com
Podman a imagem `ocipizza/admin-service`, identificada pelo hash completo do
commit. O stage `deliver-admin-service-image` entrega esse output ao repositório
privado `ocipizza/admin-service` no OCIR, usando como tag o hash completo do
commit exportado pelo Build Spec na variável `BUILDRUN_HASH`.

## Execução

Execute sempre a partir deste diretório:

```bash
cd $HOME/ocn-ocipizza/terraform
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan
terraform apply
```

Revise o plano antes do apply, principalmente operações que substituam ou
removam recursos. Não administre esta mesma infraestrutura com outro state
Terraform simultaneamente.
