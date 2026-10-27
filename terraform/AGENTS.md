# Instruções para agentes — Terraform da OCI Pizza

Este arquivo define as regras para alterar a infraestrutura da OCI Pizza. O
Terraform é usado para provisionar a arquitetura didática multi-região nas
regiões `sa-saopaulo-1` (GRU) e `sa-vinhedo-1` (VCP).

## Princípios gerais

- Entenda a topologia existente antes de alterar qualquer recurso.
- Consulte `terraform/README.md` e os arquivos do módulo afetado.
- Faça alterações pequenas, isoladas e fáceis de revisar.
- Preserve alterações existentes do usuário e de outros agentes.
- Não execute `terraform destroy` sem solicitação explícita.
- Não execute `git reset`, `git checkout`, `git clean`, commit, push ou merge.
- Não armazene OCIDs sensíveis, chaves privadas, tokens ou credenciais no código.
- Não crie arquivos fora do repositório.

## Organização dos arquivos

O root module é composto por:

- `gru.tf`: instancia os módulos na região GRU;
- `vcp.tf`: instancia os módulos na região VCP;
- `providers.tf`: declara os aliases `oci.gru` e `oci.vcp`;
- `variables.tf`: entradas compartilhadas do root module;
- `locals.tf`: somente valores globais compartilhados;
- `outputs.tf`: outputs publicados pelo root module;
- `remote-peering.tf`: conexão entre as regiões.

Cada recurso deve permanecer no módulo responsável por ele. Não coloque
recursos de uma VCN diretamente no root module.

Os módulos regionais reutilizáveis ficam em diretórios próprios:

- `vcn-firewall/`, `vcn-oke/`, `vcn-ci/`, `vcn-db/` e `vcn-services/`:
  redes, gateways, sub-redes, Route Tables e Security Lists;
- `vcn-onpremises/`: VCN de laboratório em GRU para simular a rede on-premises
  de uma futura conexão VPN;
- `oke/`: cluster OKE e node pool;
- `compute-firewall/`: instâncias de firewall e cloud-init;
- `nlb/`: Network Load Balancer e backends;
- `drg/`: DRG, attachments, tabelas e distribuições de rotas;
- `nosql/`, `objectstorage/`, `queue/`, `valkey/`, `logging/`,
  `email-delivery/`, `dns/` e `public-ip/`: serviços gerenciados da OCI.

Cada módulo deve ter, quando aplicável, `providers.tf`, `variables.tf`,
`locals.tf`, arquivos de recursos separados e `outputs.tf`.

## Cabeçalho obrigatório

Todo arquivo Terraform deve começar com o caminho relativo do arquivo:

```text
#
# modules/example/resource.tf
#
```

Para arquivos diretamente em `terraform/`, use somente o nome do arquivo:

```text
#
# gru.tf
#
```

## Configuração multi-região

- GRU e VCP devem usar o mesmo módulo parametrizado.
- Não duplique a implementação de um recurso apenas por causa da região.
- Use `region_key` para selecionar a configuração regional em `locals.tf`.
- Mantenha CIDRs, nomes, DNS labels, shapes, limites e regras em `locals.tf`.
- Use `providers = { oci = oci.gru }` ou `providers = { oci = oci.vcp }`
  nas chamadas dos módulos.
- Recursos que dependem de outro módulo devem receber os IDs por variáveis,
  criando dependências explícitas no grafo Terraform.

## Rede e roteamento

- Cada sub-rede deve ter sua própria Route Table e Security List quando essa
  for a regra definida para a VCN.
- Não introduza Network Security Groups sem solicitação explícita.
- Utilize um único DHCP Options por VCN, salvo decisão documentada no módulo.
- Não crie rotas estáticas duplicadas ou conflitantes para o mesmo destino.
- Use `SERVICE_CIDR_BLOCK` para destinos do Oracle Services Network.
- O tráfego encaminhado ao firewall deve respeitar a cadeia DRG → VCN Route
  Table → NLB → Compute Firewall.
- O NLB do firewall deve preservar origem e destino quando essa opção estiver
  definida no módulo.
- Ao alterar rotas, verifique também o caminho de retorno e as regras de
  Security List.
- A VCN `vcn-onpremises/` possui uma única sub-rede pública, Security List
  stateful sem ingressos e rota padrão para o Internet Gateway; ela não deve
  ser anexada ao DRG. Não crie uma réplica em VCP sem solicitação explícita.

## OKE

- O endpoint do Kubernetes API deve permanecer na sub-rede `kube_api`.
- Load Balancers públicos devem usar a sub-rede `loadbalancer`.
- Worker nodes devem usar a sub-rede privada `worker_nodes`.
- O cluster atual usa `BASIC_CLUSTER` e `FLANNEL_OVERLAY`.
- O node pool padrão possui dois `VM.Standard.A1.Flex`, com 3 OCPUs e 6 GB
  de memória por node.
- Não altere a versão do Kubernetes sem verificar a compatibilidade da imagem
  ARM, do provider OCI e das regiões GRU e VCP.
- Mudanças no OKE devem considerar rotas para o Service Gateway, DRG,
  endpoints privados e requisitos de registro dos worker nodes.

## Segurança e credenciais

- Nunca versione chaves privadas, arquivos OCI config, senhas ou tokens.
- Chaves públicas devem ser referenciadas por variável ou arquivo ignorado,
  nunca acompanhadas da chave privada.
- Prefira Instance Principal, Bastion e políticas IAM de menor privilégio,
  conforme o componente permitir.
- Não torne buckets privados públicos sem solicitação explícita.
- Não amplie ingressos de `0.0.0.0/0` sem avaliar o impacto e documentar a
  necessidade no módulo.

## Nomenclatura e legibilidade

- Use nomes em inglês no código Terraform e comentários em português do Brasil.
- Preserve os nomes definidos pela arquitetura, como `vcn-firewall`, `sgw`,
  `ngw`, `igw`, `rt-to-firewall-ip` e `notifications-queue`.
- Prefira arquivos pequenos e com uma responsabilidade clara:
  `vcn.tf`, `subnet.tf`, `route-table.tf`, `security-list.tf`, `gateway.tf`.
- Comentários devem explicar intenção arquitetural, dependências OCI ou
  limitações relevantes; não repita literalmente o código.
- Mantenha indentação e espaçamento produzidos por `terraform fmt`.

## Alterações e estado Terraform

- Não altere nomes ou endereços de recursos sem avaliar impacto no state.
- Não adicione blocos `moved` quando os recursos foram criados do zero ou o
  usuário informou que não deseja migração de state.
- Antes de remover um recurso, confirme se ele está no state e se há recursos
  dependentes na Console OCI.
- Erros de exclusão como `security list is in use` normalmente indicam
  dependências criadas fora do state ou recursos OCI ainda ativos; investigue
  antes de repetir operações destrutivas.
- Não edite manualmente `terraform.tfstate`.

## Validação obrigatória

Após alterações Terraform:

```bash
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform validate
terraform -chdir=terraform plan -var='compartment_id=<ocid>'
```

Se `validate` ou `plan` não puderem ser executados por falta de credenciais,
provider ou conectividade, informe exatamente o comando, o erro e qual parte
foi validada com sucesso. Não declare a infraestrutura pronta apenas porque o
arquivo foi formatado.

## Documentação

Quando uma alteração modificar a arquitetura, atualize `terraform/README.md`
com a responsabilidade do módulo e o fluxo de rede afetado. Mantenha este
`AGENTS.md` focado em regras de trabalho para agentes; detalhes operacionais
dos recursos devem permanecer no README e nos comentários dos arquivos.
