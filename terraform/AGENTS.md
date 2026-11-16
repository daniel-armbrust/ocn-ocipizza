# Terraform — OCI Pizza

Este diretório contém o único root module Terraform responsável por provisionar
e automatizar o ambiente do OCI Pizza na Oracle Cloud Infrastructure (OCI).

As regras gerais do `AGENTS.md` da raiz do repositório continuam aplicáveis.
Este arquivo complementa essas regras para qualquer alteração em `terraform/`.

## Estrutura

- `terraform/` é a raiz do código Terraform e deve ser o diretório de execução
  dos comandos `terraform init`, `terraform plan` e `terraform apply`.
- Os arquivos `.tf` da raiz compõem os recursos e os módulos regionais.
- Os subdiretórios organizam módulos locais por responsabilidade, como VCNs,
  DRG, firewall, OKE, OCI Cache, NoSQL, Object Storage, DNS e Logging.
- IAM, OCI DevOps, OCIR, Vault, Build Pipelines e Deployment Pipelines também
  devem ser declarados neste mesmo root module.
- Não recriar os antigos diretórios `terraform/bootstrap` ou
  `terraform/infrastructure`.

Todos os recursos pertencem à mesma configuração e ao mesmo state Terraform.
Alterações estruturais devem preservar os endereços dos recursos existentes
sempre que isso evitar substituições desnecessárias.

### Organização dos arquivos Terraform

- Todos os blocos `data` devem ficar no arquivo `datasource.tf` do respectivo
  módulo ou root module.
- Todos os blocos `locals` devem ficar no arquivo `locals.tf` do respectivo
  módulo ou root module.
- Blocos `terraform_data` são resources, não data sources. Eles devem ficar no
  arquivo relacionado à responsabilidade que automatizam, como `vault.tf`.
- Alterar apenas o arquivo que contém o bloco, sem mudar seu endereço lógico,
  não exige `moved` block nem alteração do state.

### Organização dos Shell Scripts

Todo Shell Script deve manter obrigatoriamente esta ordem:

1. variáveis globais e constantes;
2. funções;
3. restante do programa e execução principal.

Não declarar funções depois do início da execução principal nem intercalar
funções com comandos do fluxo principal. Toda função deve possuir um comentário
imediatamente acima de sua declaração, explicando de forma objetiva sua
responsabilidade.

## Arquitetura

- A infraestrutura é multirregião e utiliza `sa-saopaulo-1` (GRU) e
  `sa-vinhedo-1` (VCP).
- Os providers regionais devem permanecer explícitos por meio dos aliases
  `oci.gru` e `oci.vcp`.
- Toda instanciação de módulo regional deve permanecer em `gru.tf` ou `vcp.tf`,
  conforme a região. Não criar arquivos `.tf` separados na raiz para chamar
  módulos regionais.
- A arquitetura de rede utiliza Hub-and-Spoke com DRGs regionais, Remote
  Peering e inspeção de tráfego pela VCN-FIREWALL.
- As VCNs de OKE, banco de dados e serviços possuem responsabilidades
  separadas e não devem ser consolidadas sem decisão arquitetural explícita.
- A VCN-SERVICES hospeda os serviços compartilhados, os futuros Container
  Instances e a sub-rede pública destinada ao Load Balancer desses workloads.
- Os clusters OKE, serviços gerenciados e componentes da aplicação devem
  continuar preparados para operação nas duas regiões.

## Responsabilidades do Terraform

O root module deve administrar:

- IAM necessário à infraestrutura, aos workloads e ao OCI DevOps;
- redes, segurança, conectividade, Compute, NLBs e OKE;
- NoSQL, Object Storage, Queue, OCI Cache, DNS, Email Delivery e Logging;
- recursos do OCI DevOps, conexões com o GitHub, artefatos, OCIR, Vault,
  Build Pipelines, Deployment Pipelines e ambientes de deployment;
- outputs necessários às pipelines e às etapas posteriores de automação.

A configuração interna do Kubernetes e o deployment dos microsserviços são
responsabilidades das pipelines do OCI DevOps e dos arquivos existentes em
`kubernetes/`. O Terraform cria e configura os recursos OCI usados por essas
pipelines, mas não deve incorporar manifests Kubernetes ao state sem uma
decisão explícita.

## Diretrizes

- Utilizar o provider oficial `oracle/oci`.
- Manter o código declarativo, idempotente e organizado em módulos locais
  focados em uma responsabilidade.
- Evitar duplicação desnecessária entre GRU e VCP; parametrizar diferenças
  regionais com variáveis e locals.
- Utilizar variáveis, referências a recursos e data sources em vez de OCIDs
  fixos.
- Expor por outputs somente os valores necessários a integrações e pipelines.
- Não publicar segredos em outputs, arquivos `.tfvars`, código ou state.
- Armazenar PATs, tokens, senhas e outras credenciais no OCI Vault quando
  precisarem ser consumidos por serviços OCI.
- Aplicar o princípio do menor privilégio nas policies IAM.
- Criar policies IAM no root compartment quando o escopo ou o serviço exigir,
  limitando os statements aos compartments e recursos necessários.
- Não versionar arquivos Terraform State, planos salvos, chaves privadas ou
  diretórios `.terraform`.
- Preservar alterações existentes e não substituir recursos apenas para
  simplificar uma refatoração.

## State e execução

- Existe um único state associado ao root module `terraform/`.
- Não executar a mesma configuração simultaneamente com states diferentes.
- Não mover, importar ou remover recursos do state sem solicitação explícita e
  revisão prévia do impacto.
- Não executar `terraform apply` ou `terraform destroy` sem autorização
  explícita do usuário.
- Antes de um apply, revisar especialmente qualquer ação de `destroy` ou
  `replace` apresentada pelo plano.

## Validação

Após alterações, executar quando aplicável:

```bash
cd terraform
terraform fmt -recursive
terraform validate
terraform plan
```

O `terraform plan` deve ser apenas de leitura e não autoriza um apply. Se uma
validação não puder ser concluída por indisponibilidade do provider, ausência
de credenciais ou restrição do ambiente, registrar claramente essa limitação.

Antes de implementar alterações, consultar o `terraform/README.md`, os módulos
afetados e os contratos existentes entre outputs, IAM, pipelines e workloads.
Atualizar o README quando houver mudança de arquitetura, configuração,
variáveis, responsabilidades ou fluxo de execução.
