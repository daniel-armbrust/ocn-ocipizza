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

A zona DNS privada `ocipizza.internal` existe de forma independente em GRU e
VCP. Cada região possui sua própria Private View, associada aos resolvers das
VCNs de firewall, OKE, banco de dados e serviços. As sub-redes dessas VCNs
utilizam `VcnLocalPlusInternet` nos DHCP Options e, por isso, consultam
automaticamente o resolver regional e os registros da zona privada
correspondente. A VCN on-premises simulada não consulta essa zona.

Os registros `mysql-write.ocipizza.internal` e
`mysql-read.ocipizza.internal` abstraem os endpoints privados dos bancos. O
registro de escrita aponta para o primary de GRU nas duas zonas regionais. O
registro de leitura aponta para o MySQL local: primary em GRU e secondary
read-only em VCP. Em um desastre, a promoção de VCP exige atualizar o destino
de `mysql-write` para o endpoint promovido.

A VCN-OKE de cada região possui sub-redes próprias para Load Balancers,
worker nodes, endpoint privado do Kubernetes API e pods. A sub-rede privada de
pods reserva endereços para o futuro cluster Enhanced com OCI VCN-Native Pod
Networking; ela não é consumida pelos clusters Basic com Flannel atuais.

Os códigos OKE são separados por arquitetura em `oke/basic-flannel/` e
`oke/enhanced-virtual-nodes/`. O primeiro módulo cria os clusters Basic atuais
com Flannel e Managed Nodes. O segundo diretório está reservado para a futura
implementação dos clusters Enhanced com Virtual Nodes. Os blocos alternativos
permanecem documentados e comentados em `gru.tf` e `vcp.tf`; somente uma
arquitetura OKE deve ficar habilitada por região.

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

O OCI Cache utiliza uma topologia cross-region active-passive. O cluster de
GRU é o primary e aceita leituras e escritas. O cluster de VCP é o secondary,
recebe replicação assíncrona e aceita somente leituras. Os dois clusters são
NONSHARDED, possuem 8 GB por nó e usam Configuration Sets regionais com os
mesmos parâmetros exigidos pela replicação. A conectividade de replicação é
gerenciada pela OCI e não utiliza o Remote Peering das VCNs.

O script `vault/scripts/redis-secrets.sh` gera credenciais independentes para
`admin-service` e `frontend-service` nos ambientes `homol` e `prod`. O texto
claro fica exclusivamente no Vault de GRU; somente o hash SHA-256 é enviado
ao OCI Cache. Em cada região, o script cria os quatro OCI Cache Users ausentes,
reutiliza os usuários ativos e os associa ao cluster regional. Os usuários
possuem somente as categorias de comandos necessárias à persistência de
sessões, sem comandos administrativos.

Os parâmetros internos dos Configuration Sets são aplicados durante a criação
e ignorados em atualizações posteriores pelo Terraform. A OCI não permite
remover ou substituir uma configuração customizada enquanto ela estiver
associada a um cluster ativo. Mudanças nesses parâmetros exigem um procedimento
controlado de desassociação ou recriação dos clusters.

Cada cluster possui apenas um nó para reduzir o custo do ambiente didático.
Essa escolha mantém a replicação entre GRU e VCP, mas não fornece redundância
dentro de cada região. Para workloads de produção, a OCI recomenda pelo menos
três nós por cluster.

A replicação não fornece failover automático. Em um desastre regional, o
secondary de VCP deve ser convertido operacionalmente em standalone antes de
receber escritas. Um switchover também exige atualização posterior dos papéis
no Terraform antes de um novo `apply`, para que o código continue refletindo a
topologia efetiva.

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
| `TF_VAR_ocir_username` | Sim | — | Username completo usado pelas pipelines para autenticação no OCIR. |
| `TF_VAR_ocir_auth_token` | Sim | — | Auth Token armazenado no Vault para criar o `ocir-secret` no OKE. |
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
export TF_VAR_ocir_username="namespace/usuario"
export TF_VAR_ocir_auth_token="auth_token_substitua"
```

As variáveis de chaves recebem somente o conteúdo das chaves públicas. Nunca
adicione chaves privadas, tokens ou outros segredos ao repositório.

`TF_VAR_github_pat` e `TF_VAR_ocir_auth_token` são sensíveis e não aparecem
nos outputs. O Terraform armazena somente seus hashes no state para detectar
mudanças; os conteúdos são enviados aos scripts do Vault por variáveis de
ambiente e armazenados diretamente nos Secrets.

## IAM

O arquivo `iam.tf` cria somente as identidades e policies consumidas pelos
recursos do OCI Pizza:

- `ocipizza-instances`: reúne Compute Instances e Container Instances do
  compartment da aplicação e permite aos workloads consumir NoSQL, Object
  Storage, Queue, Secrets, Logging e OCIR;
- `ocipizza-devops`: reúne os resource principals de build pipelines,
  deployment pipelines, repositórios e conexões do OCI DevOps, permitindo
  construir, publicar e implantar os artefatos, além de carregar os dados e
  objetos de demonstração nos recursos previamente criados pelo Terraform;
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

## Vault e secrets da aplicação

O módulo `vault/` chama o script idempotente `vault.sh` para criar em São
Paulo o Vault `ocipizza-vault`, uma chave AES de 256 bits protegida por HSM e
o Secret `ocipizza-github-pat`. Esses recursos são criados pela OCI CLI e ficam fora do
state do Terraform. O Secret recebe o PAT informado por `TF_VAR_github_pat` e
é referenciado pela conexão do OCI DevOps com o GitHub.

O mesmo módulo gera diretamente no Vault, sem registrar o conteúdo no state:

- chaves independentes de sessão e CSRF para `admin-service` e
  `frontend-service`, nos ambientes `homol` e `prod`;
- um par de chaves RSA JWT do `user-service` para cada ambiente;
- username e Auth Token usados pelas pipelines para criar o `ocir-secret` nos
  clusters OKE.

Os scripts mantêm os secrets existentes para evitar rotação acidental durante
novos applies. A futura automação do banco de dados está reservada no arquivo
vazio `database-secrets.sh`. As credenciais e os usuários do OCI Cache são
administrados por `redis-secrets.sh`.

Quando os recursos já existem, os scripts os reutilizam. Se o PAT mudar, uma
nova versão do Secret é criada somente quando o conteúdo for diferente. No
`terraform destroy`, os scripts são chamados em modo de destruição, mas não
excluem o Vault, a chave nem o Secret. Assim, esses recursos persistentes podem
ser usados novamente por um próximo `terraform apply`.

Esse fluxo requer OCI CLI, `jq`, `base64` e OpenSSL instalados na máquina que
executa o Terraform. A autenticação usada pelos scripts é a mesma configuração
local da OCI descrita na seção de autenticação.

## MySQL HeatWave

O módulo `mysql/` cria um DB System standalone `MySQL.2` independente em cada
região. GRU é preparado como primary read-write e VCP como secondary read-only.
Os DB Systems começam com 50 GB, possuem expansão automática até 500 GB,
backups por sete dias e Point in Time Recovery.

O script `vault/scripts/database-secrets.sh` cria e preserva dois Secrets no
Vault para a infraestrutura: um para o administrador e outro para o usuário
exclusivo de replicação. Ele também mantém um Secret separado e com menor
privilégio para as credenciais de banco do `user-service`.
As credenciais são recuperadas pelo Terraform, marcadas como sensíveis e, por
decisão deste ambiente didático, permanecem no state. O state deve receber os
mesmos controles de acesso aplicados a um segredo.

O Terraform não conecta ao banco, não cria usuários internos e não ativa o
canal de replicação. Um pipeline exclusivo de bootstrap do MySQL será
responsável por criar `ocipizza_replicator` com os privilégios mínimos, criar
os usuários e schemas da aplicação, preparar a cópia inicial dos dados e
configurar a replicação assíncrona de GRU para VCP. Assim, a máquina que executa
o Terraform não precisa do cliente MySQL nem de conectividade direta com os
endpoints privados dos bancos.

A lógica operacional fica em `mysql/bootstrap/`. O Build Spec deve ser
executado pelo OCI DevOps somente depois do `terraform apply` e antes dos
bootstraps dos microsserviços. Ele lê as credenciais administrativa e de
replicação no Vault por Resource Principal, cria o usuário
`ocipizza_replicator`, cria ou reutiliza o canal `mysql-gru-to-vcp` e aguarda o
estado `ACTIVE`. Os parâmetros da Build Pipeline `bootstrap-ocipizza` fornecem os OCIDs dos
dois DB Systems e dos dois Secrets; nenhum desses valores fica fixado nos
scripts.

As regiões não ficam fixadas no Build Spec. Os scripts usam
`sa-saopaulo-1` como valor padrão de `MYSQL_PRIMARY_REGION` e
`sa-vinhedo-1` como valor padrão de `MYSQL_SECONDARY_REGION`. A Build Pipeline
pode substituir qualquer um desses valores sem modificar os scripts.

O bootstrap acessa o primary por meio de
`mysql-write.ocipizza.internal`, configurado em `MYSQL_PRIMARY_HOST`. Esse nome
é publicado nas zonas privadas das duas regiões e evita depender do hostname
nativo de uma VCN específica. O parâmetro pode ser substituído em um Manual
Run sem alterar os scripts.

O stage `bootstrap-user-service` é executado depois do stage `bootstrap-mysql`.
Ele utiliza Resource Principal para ler no Vault as credenciais administrativa
e específica do serviço, criar o schema `users`, manter o usuário da aplicação
e aplicar as migrations existentes do Alembic.

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

O módulo `ocir/` cria repositórios privados dos microsserviços em São Paulo e
Vinhedo. Os módulos `ocir_gru` e `ocir_vcp` mantêm a mesma estrutura regional
para que as Build Pipelines possam publicar cada imagem, com a mesma tag, nos
dois registries Standard. As tags são baseadas no identificador da execução do
build para distinguir cada versão produzida.

A configuração de imutabilidade não é declarada porque a API do OCI Container
Registry ainda não permite definir `is_immutable` na criação do repositório.
Não é utilizado Pull-Through Cache; portanto, a publicação em VCP não depende
de username ou Auth Token de um usuário OCI.

## OCI Artifact Registry

O módulo `artifact-registry/` cria um repositório Generic e imutável em cada
região. `ocipizza-kubernetes-manifests-gru` recebe os manifests renderizados
para São Paulo, enquanto `ocipizza-kubernetes-manifests-vcp` recebe os manifests
renderizados para Vinhedo. As Build Pipelines publicarão versões únicas desses
arquivos; o Terraform administra somente os repositórios e não armazena o
conteúdo dos manifests no state.

Os artefatos devem ser organizados por serviço e ambiente dentro de cada
repositório, por exemplo `pizza-service/homol` e `pizza-service/prod`. A versão
do Generic Artifact deverá identificar de forma única a execução ou o commit
que produziu o manifesto, pois uma versão publicada não pode ser sobrescrita.

O namespace único da tenancy é consultado uma vez no root module, em
`datasource.tf`, e repassado aos módulos `objectstorage/` e `devops/`. Esse
valor é usado tanto pelos buckets e sua replicação quanto para compor a URL do
repositório OCIR consumida pela build pipeline.

Os outputs `ocir_pizza_service_repository_id`,
`ocir_pizza_service_repository_namespace` e
`ocir_pizza_service_repository_url` fornecem os valores necessários para a
futura configuração do deployment artifact e do stage `DELIVER_ARTIFACT`.

### Pipeline de bootstrap

O submódulo `devops/bootstrap/` cria a Build Pipeline
`bootstrap-ocipizza`. O Managed Build `bootstrap-pizza-service` executa
`services/pizza-service/bootstrap_spec.yaml` diretamente.

Cada serviço deve possuir um submódulo próprio em `devops/bootstrap/` e um
Managed Build próprio nessa pipeline. Por enquanto, somente o submódulo
`devops/bootstrap/pizza-service/` está configurado. O parâmetro
`NOSQL_COMPARTMENT_ID` recebe como padrão o compartment administrado pelo
Terraform e é disponibilizado ao script de bootstrap. Os demais providers e
nomes de recursos são definidos no Build Spec do serviço.

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
