# Infraestrutura da OCI Pizza

## Propósito do diretório

O diretório `terraform/infrastructure` contém o root module e os módulos locais que declaram a infraestrutura completa da OCI Pizza na Oracle Cloud Infrastructure (OCI).

A infraestrutura é distribuída entre as regiões `sa-saopaulo-1` (GRU) e `sa-vinhedo-1` (VCP) e abrange rede, conectividade entre regiões, segurança, balanceamento, OKE, serviços gerenciados, DNS e observabilidade. Os recursos básicos usados para hospedar e administrar essa infraestrutura pertencem ao diretório `terraform/bootstrap`.

## Arquivos do root module

| Arquivo | Função |
| --- | --- |
| `.terraform.lock.hcl` | Registra as versões selecionadas dos providers Terraform. |
| `providers.tf` | Declara os providers OCI de GRU e VCP. |
| `variables.tf` | Declara as entradas compartilhadas pelo root module. |
| `locals.tf` | Centraliza nomes, CIDRs e configurações regionais. |
| `gru.tf` | Compõe os módulos e recursos da região de São Paulo. |
| `vcp.tf` | Compõe os módulos e recursos da região de Vinhedo. |
| `remote-peering.tf` | Declara o peering remoto entre os DRGs regionais. |
| `dns.tf` | Compõe a zona DNS pública e seus registros. |
| `outputs.tf` | Publica identificadores e atributos da infraestrutura. |
| `iam.tf` | Arquivo reservado para recursos IAM da infraestrutura; atualmente está vazio. |
| `README.md` | Documenta o propósito do diretório e seus arquivos. |

## Arquivos comuns aos módulos

| Arquivo | Função |
| --- | --- |
| `providers.tf` | Declara os providers exigidos pelo módulo. |
| `variables.tf` | Define as entradas aceitas pelo módulo. |
| `locals.tf` | Organiza valores derivados e configurações internas. |
| `datasource.tf` | Consulta dados existentes necessários aos recursos. |
| `outputs.tf` | Expõe identificadores e atributos produzidos pelo módulo. |

## Módulos de rede

### `vcn-firewall/`

Declara a VCN de inspeção e as sub-redes privadas dos firewalls e do NLB.

| Arquivo | Função |
| --- | --- |
| `vcn.tf` | Declara a VCN de firewall. |
| `gateway.tf` | Declara os gateways da VCN. |
| `dhcp.tf` | Declara as opções DHCP. |
| `route-table.tf` | Declara as tabelas e regras de roteamento. |
| `security-list.tf` | Declara as regras de segurança das sub-redes. |
| `subnet.tf` | Declara as sub-redes do NLB e dos firewalls. |
| `datasource.tf`, `locals.tf`, `providers.tf`, `variables.tf`, `outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente. |

### `vcn-oke/`

Declara a VCN do OKE e as sub-redes do load balancer, worker nodes e Kubernetes API.

| Arquivo | Função |
| --- | --- |
| `vcn.tf` | Declara a VCN do OKE. |
| `gateway.tf` | Declara os gateways da VCN. |
| `dhcp.tf` | Declara as opções DHCP. |
| `route-table.tf` | Declara as tabelas e regras de roteamento. |
| `security-list.tf` | Declara as regras de segurança do OKE. |
| `subnet.tf` | Declara as três sub-redes utilizadas pelo OKE. |
| `datasource.tf`, `locals.tf`, `providers.tf`, `variables.tf`, `outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente. |

### `vcn-db/`

Declara a VCN e a sub-rede privada destinadas ao MySQL.

| Arquivo | Função |
| --- | --- |
| `vcn.tf` | Declara a VCN de banco de dados. |
| `dhcp.tf` | Declara as opções DHCP. |
| `route-table.tf` | Declara o roteamento da sub-rede. |
| `security-list.tf` | Declara as regras de segurança do banco. |
| `subnet.tf` | Declara a sub-rede privada do MySQL. |
| `locals.tf`, `providers.tf`, `variables.tf`, `outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente. |

### `vcn-ci/`, `vcn-services/` e `vcn-onpremises/`

Declaram, respectivamente, as redes de Container Instances, serviços compartilhados e ambiente on-premises simulado.

| Diretório e arquivo | Função |
| --- | --- |
| `vcn-ci/vcn.tf`, `vcn-services/vcn.tf`, `vcn-onpremises/vcn.tf` | Declaram as respectivas VCNs. |
| `*/gateway.tf` | Declara os gateways de cada VCN. |
| `*/dhcp.tf` | Declara as opções DHCP de cada VCN. |
| `*/route-table.tf` | Declara as tabelas e regras de roteamento. |
| `*/security-list.tf` | Declara as regras de segurança das sub-redes. |
| `*/subnet.tf` | Declara as sub-redes de cada VCN. |
| `vcn-ci/datasource.tf`, `vcn-services/datasource.tf` | Consultam dados existentes necessários aos módulos. |
| `*/locals.tf`, `*/providers.tf`, `*/variables.tf`, `*/outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente. |

## Módulos de conectividade e segurança

### `drg/`

Declara o Dynamic Routing Gateway e a conectividade das VCNs regionais.

| Arquivo | Função |
| --- | --- |
| `drg.tf` | Declara o DRG regional. |
| `attachments.tf` | Anexa as VCNs ao DRG. |
| `route-table.tf` | Declara as tabelas de rotas do DRG. |
| `route-rule.tf` | Declara as regras das tabelas de rotas. |
| `route-distribution.tf` | Declara as distribuições de rotas. |
| `route-distribution-statement.tf` | Declara as instruções de importação de rotas. |
| `vcn-route-table.tf` | Declara as rotas das VCNs direcionadas ao DRG. |
| `locals.tf`, `providers.tf`, `variables.tf`, `outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente. |

### `compute-firewall/`

Declara as instâncias Compute responsáveis pela inspeção do tráfego regional.

| Arquivo | Função |
| --- | --- |
| `instance.tf` | Declara os firewalls e suas interfaces de rede. |
| `config/squid.conf` | Define a configuração do proxy Squid. |
| `config/README.md` | Documenta os arquivos de configuração. |
| `scripts/configure-firewall.sh` | Configura o firewall durante sua inicialização. |
| `scripts/README.md` | Documenta os scripts do módulo. |
| `keys/README.md` | Documenta a finalidade das chaves SSH. |
| `datasource.tf`, `locals.tf`, `providers.tf`, `variables.tf`, `outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente. |

### `nlb/`

Declara o Network Load Balancer privado que distribui tráfego entre os firewalls.

| Arquivo | Função |
| --- | --- |
| `nlb.tf` | Declara o NLB privado. |
| `backendset.tf` | Declara o conjunto de backends. |
| `backend.tf` | Associa os firewalls ao backend set. |
| `listener.tf` | Declara o listener do NLB. |
| `datasource.tf`, `locals.tf`, `providers.tf`, `variables.tf`, `outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente. |

## Módulo de Kubernetes

### `oke/`

Declara os clusters OKE regionais e seus node pools privados.

| Arquivo | Função |
| --- | --- |
| `cluster.tf` | Declara o cluster OKE e seus endpoints. |
| `node-pool.tf` | Declara o node pool e os worker nodes. |
| `scripts/oke-cloudinit.sh` | Define a inicialização complementar dos worker nodes. |
| `keys/README.md` | Documenta a finalidade da chave SSH dos workers. |
| `datasource.tf`, `locals.tf`, `providers.tf`, `variables.tf`, `outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente. |

## Módulos de serviços gerenciados

| Módulo e arquivo | Função |
| --- | --- |
| `dns/zone.tf` | Declara a zona DNS pública. |
| `dns/records.tf` | Declara os registros da aplicação e de validação de e-mail. |
| `public-ip/reserved-ip.tf` | Declara o IP público reservado do load balancer regional. |
| `email-delivery/email-domain.tf` | Declara o domínio de envio de e-mail. |
| `email-delivery/dkim.tf` | Declara a chave DKIM do domínio. |
| `email-delivery/sender.tf` | Declara o remetente autorizado. |
| `nosql/table-pizzas.tf` | Declara a tabela de pizzas. |
| `nosql/table-pizzas-replica.tf` | Declara a réplica da tabela de pizzas. |
| `nosql/table-delivery-areas.tf` | Declara a tabela de áreas de entrega. |
| `nosql/table-delivery-areas-replica.tf` | Declara a réplica da tabela de áreas de entrega. |
| `nosql/table-orders.tf` | Declara a tabela de pedidos. |
| `nosql/table-orders-replica.tf` | Declara a réplica da tabela de pedidos. |
| `objectstorage/bucket-pizza-images.tf` | Declara o bucket privado de imagens. |
| `objectstorage/bucket-pizza-images-replica.tf` | Declara a replicação regional do bucket. |
| `queue/queue.tf` | Declara a fila regional da aplicação. |
| `valkey/cluster.tf` | Declara o cluster privado OCI Cache com engine Valkey. |
| `logging/log-group.tf` | Declara o grupo regional de logs. |
| `logging/logs.tf` | Declara os logs dos microsserviços. |
| `*/datasource.tf` | Consulta dados existentes nos módulos que necessitam dessas informações. |
| `*/locals.tf`, `*/providers.tf`, `*/variables.tf`, `*/outputs.tf` | Implementam as responsabilidades comuns descritas anteriormente em cada módulo. |
