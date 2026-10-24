# OCI Pizza — Terraform de infraestrutura

Esta configuração Terraform provisiona a infraestrutura da OCI Pizza nas regiões
`sa-saopaulo-1` e `sa-vinhedo-1`. As implementações são reutilizadas, mas as
configurações regionais são declaradas explicitamente em `locals.tf`. Isso
facilita a leitura da arquitetura multi-região e a documentação de diferenças
entre GRU e VCP.

## Estrutura

```text
terraform/
├── gru.tf                  # Chama os módulos da região São Paulo
├── vcp.tf                  # Chama os módulos da região Vinhedo
├── remote-peering.tf       # RPC entre GRU e VCP
├── locals.tf               # Valores globais, como nomes das regiões
├── providers.tf            # Providers OCI GRU e VCP
├── variables.tf            # Entradas externas, como compartment e DRG
├── outputs.tf              # IDs publicados pelo root module
├── vcn-firewall/
│   ├── locals.tf            # Configurações explícitas de GRU e VCP
│   ├── vcn.tf               # VCN
│   ├── gateway.tf           # NAT Gateway e Service Gateway
│   ├── dhcp.tf              # Único DHCP Options da VCN
│   ├── route-table.tf       # Route Tables do NLB e do firewall
│   ├── security-list.tf     # Security Lists das sub-redes privadas
│   └── subnet.tf            # Sub-redes NLB e firewall
├── vcn-oke/
│   ├── locals.tf            # Configurações explícitas de GRU e VCP
│   ├── vcn.tf               # VCN-OKE
│   ├── gateway.tf           # Service Gateway
│   ├── dhcp.tf              # DHCP Options
│   ├── route-table.tf       # Route Tables das sub-redes
│   ├── security-list.tf     # Security Lists das sub-redes
│   └── subnet.tf            # Sub-redes LB, workers e Kubernetes API
├── oke/
│   ├── locals.tf             # Nome, CNI, shape e capacidade do cluster
│   ├── datasource.tf         # Availability Domain e imagens ARM compatíveis
│   ├── cluster.tf             # Cluster OKE com API privado e LB público
│   ├── node-pool.tf           # Dois workers A1 Flex na sub-rede privada
│   ├── providers.tf           # Provider OCI exigido pelo módulo
│   ├── variables.tf           # VCN, sub-redes e versão do Kubernetes
│   └── outputs.tf             # IDs do cluster e do node pool
├── vcn-db/
    ├── locals.tf            # Configurações explícitas de GRU e VCP
    ├── vcn.tf               # VCN-DB
    ├── gateway.tf           # Service Gateway
    ├── dhcp.tf              # DHCP Options
    ├── route-table.tf       # Route Table da sub-rede MySQL
    ├── security-list.tf     # Security List da sub-rede MySQL
    └── subnet.tf            # Sub-rede privada do MySQL
├── vcn-ci/
│   ├── locals.tf            # Configurações explícitas de GRU e VCP
│   ├── vcn.tf               # VCN-CI
│   ├── gateway.tf           # Service Gateway
│   ├── dhcp.tf              # DHCP Options
│   ├── route-table.tf       # Route Tables das sub-redes
│   ├── security-list.tf     # Security Lists das sub-redes
│   └── subnet.tf            # Sub-redes privadas do Container Instances
├── vcn-services/
│   ├── locals.tf             # Configuração regional da VCN-SERVICES
│   ├── vcn.tf                # VCN de serviços compartilhados
│   ├── gateway.tf            # Service Gateway
│   ├── dhcp.tf               # DHCP Options
│   ├── route-table.tf        # Rota padrão para DRG e Service Gateway
│   ├── security-list.tf      # Security List da sub-rede
│   └── subnet.tf             # Sub-rede privada de serviços
├── nlb/
│   ├── nlb.tf                # Network Load Balancer privado
│   ├── backendset.tf         # Backend set dos firewalls
│   ├── backend.tf            # Backends do NLB
│   └── listener.tf           # Listener TCP de qualquer porta
├── nosql/
│   ├── locals.tf             # DDL e limites das tabelas
│   ├── table-pizzas.tf       # Tabela pizzas
│   ├── table-delivery-areas.tf # Tabela delivery_areas
│   ├── table-orders.tf       # Tabela orders
│   └── *-replica.tf          # Réplicas Global Active em VCP
├── objectstorage/
│   ├── bucket-pizza-images.tf         # Bucket privado de imagens
│   └── bucket-pizza-images-replica.tf # Replicação regional
├── queue/
│   └── queue.tf             # Fila notifications-queue regional
├── email-delivery/
│   ├── email-domain.tf       # Domínio de envio
│   ├── dkim.tf               # DKIM
│   └── sender.tf             # Remetente no-reply
├── dns/
│   ├── zone.tf               # Zona pública ocipizza.com.br
│   └── records.tf            # Registros regionais dos load balancers
├── public-ip/
│   └── reserved-ip.tf        # IPs públicos regionais dos load balancers
├── valkey/
│   ├── locals.tf             # Configuração regional do cluster Valkey
│   ├── cluster.tf            # Cluster privado OCI Cache com engine Valkey
│   ├── providers.tf          # Provider OCI exigido pelo módulo
│   ├── variables.tf          # Compartment, região e sub-rede do cluster
│   └── outputs.tf            # OCID e endpoints do cluster
├── logging/
│   ├── locals.tf              # Grupo, serviços e retenção dos logs
│   ├── log-group.tf           # Grupo regional loggroup-ocipizza
│   ├── logs.tf                # Logs individuais dos microsserviços
│   ├── providers.tf           # Provider OCI exigido pelo módulo
│   ├── variables.tf           # Compartment e região do grupo
│   └── outputs.tf             # OCID do grupo e dos logs
├── compute-firewall/
│   ├── locals.tf             # Imagens e shape da instância
│   ├── instance.tf            # Compute Firewall e VNIC privada
│   ├── datasource.tf          # Availability Domain e VNIC primária
│   ├── scripts/               # Cloud-init, forwarding e MASQUERADE
│   └── outputs.tf             # IDs da instância e da VNIC
└── drg/
    ├── locals.tf            # Configuração regional e attachments
    ├── drg.tf               # DRG regional
    ├── attachments.tf       # Attachments das VCNs
    ├── route-table.tf       # Tabelas do DRG, incluindo remote-peering
    ├── vcn-route-table.tf   # VCN Route Table rt-to-firewall-ip
    ├── route-rule.tf        # Regra padrão para o firewall
    ├── route-distribution.tf # Import Route Distribution
    ├── route-distribution-statement.tf # Regras de importação
    └── outputs.tf           # IDs do DRG, attachments e tabelas
```

O módulo `vcn-oke/` segue o mesmo padrão de arquivos do módulo de firewall.
Ele cria, em ambas as regiões, a sub-rede pública `loadbalancer` e as
sub-redes privadas `worker_nodes` e `kube_api`, cada uma com sua própria Route
Table e Security List.

O módulo `oke/` cria um cluster em cada região a partir da VCN-OKE
correspondente. O endpoint do Kubernetes API é privado e fica na sub-rede
`kube_api`; os Load Balancers públicos são criados na sub-rede
`loadbalancer`; e os worker nodes ficam na sub-rede privada `worker_nodes`.
O cluster usa `FLANNEL_OVERLAY`, dois worker nodes `VM.Standard.A1.Flex`, com
3 OCPUs e 6 GB de memória por node. A versão padrão é `v1.34.10`, mantida
como duas versões menores atrás da linha estável usada neste material; ela
pode ser substituída pela variável `kubernetes_version` do módulo.

O módulo `nosql/` cria as tabelas `pizzas`, `delivery_areas` e `orders` com
limites iniciais de 5 read units, 5 write units e 1 GB de armazenamento. As
tabelas principais em GRU possuem réplicas Global Active em VCP.

O módulo `objectstorage/` cria o bucket privado `pizza-images` e configura a
replicação regional dos objetos. O módulo `queue/` cria a fila
`notifications-queue` em cada região.

O módulo `email-delivery/` configura o domínio, DKIM e o remetente aprovado
`no-reply@ocipizza.com.br`. O módulo `dns/` cria a zona pública
`ocipizza.com.br`, enquanto `public-ip/` reserva os endereços regionais usados
pelos load balancers.

O módulo `vcn-db/` cria uma VCN privada para o MySQL HeatWave em cada região.
Cada VCN possui uma sub-rede exclusiva para o banco, com Route Table,
Security List, DHCP Options e Service Gateway próprios.

O módulo `vcn-ci/` cria uma VCN privada para Container Instances em cada
região. Cada VCN possui as sub-redes privadas `loadbalancer` e
`container_instances`, com Route Table e Security List próprias.

O módulo `valkey/` cria um cluster privado do OCI Cache com engine Valkey em
cada região. Os clusters são nomeados `valkey-cache-gru` e `valkey-cache-vcp`,
usam três nós não fragmentados com 2 GB por nó e ficam na sub-rede privada da
VCN-SERVICES. O módulo utiliza a versão `VALKEY_8_1`, mantida em `locals.tf`
para que a escolha do engine fique explícita e seja fácil de atualizar.

O módulo `public-ip/` reserva um endereço IPv4 regional para cada load balancer:
GRU utiliza o nome DNS `lb-gru.ocipizza.com.br` e VCP utiliza
`lb-vcp.ocipizza.com.br`. A zona DNS pública é criada pelo módulo `dns/`, que
publica os dois registros A. O endereço utilizado pelos usuários, como
`www.ocipizza.com.br`, deverá ser administrado posteriormente pelo OCI DNS
Traffic Management para permitir roteamento entre as regiões.

O módulo `logging/` cria, em cada região, o grupo `loggroup-ocipizza` e um
log customizado para cada microsserviço: pizza, admin, chatbot, delivery,
frontend, notification, order e user. A retenção inicial é de 30 dias.

O módulo `compute-firewall/` cria instâncias `VM.Standard.A1.Flex` com 2 OCPUs,
4 GB de memória e uma VNIC privada na sub-rede do firewall. O firewall recebe
o tráfego encaminhado pelo NLB, habilita forwarding IPv4 e aplica MASQUERADE
para a saída pelo NAT Gateway. O plugin `Bastion` do Oracle Cloud Agent é
habilitado para permitir sessões administrativas pelo OCI Bastion Service.

O módulo `nlb/` cria um Network Load Balancer privado, preservando origem e
distribuindo o tráfego para os backends dos firewalls.

O módulo `drg/` cria um DRG por região e anexa as VCNs de firewall, OKE, CI,
SERVICES e banco. A tabela `to-firewall-drg-rt` encaminha a rota padrão dos spokes para o
attachment do firewall. A tabela `from-firewall-drg-rt` usa uma Import Route
Distribution que aceita as rotas da VCN-OKE, da VCN-CI, da VCN-DB e de attachments de
Remote Peering, sem importar rotas da VCN-FIREWALL.

A tabela `remote-peering-drg-rt` é exclusiva dos attachments RPC e não utiliza a
tabela padrão criada automaticamente pelo OCI. Sua Import Route Distribution
aceita somente as rotas anunciadas pela VCN-FIREWALL.

O attachment da VCN-FIREWALL utiliza a VCN Route Table `rt-to-firewall-ip`,
que encaminha a rota padrão para o IP privado do NLB regional. O NLB entrega o
tráfego aos firewalls, que encaminham destinos do Oracle Services Network ao
Service Gateway e o restante ao NAT Gateway.

Na configuração atual, `rt-oke-worker-gru` possui adicionalmente uma rota
específica para o Service Gateway local. Essa rota é mais específica que a
rota padrão para o DRG e faz com que o acesso dos workers de GRU aos serviços
OCI não passe pelo firewall.

O arquivo `remote-peering.tf` cria um Remote Peering Connection em cada região,
inicia o pareamento pelo RPC de GRU e associa os attachments automáticos às
tabelas `to-firewall-drg-rt` dos respectivos DRGs.

Na VCN-FIREWALL, as sub-redes possuem as seguintes finalidades:

- `nlb`: hospeda o Network Load Balancer privado;
- `firewall`: hospeda as VNICs dos Compute Firewalls.

Cada sub-rede possui uma Route Table e uma Security List própria. A VCN usa
um único DHCP Options. Os módulos regionais recebem diretamente o OCID do DRG
criado no mesmo grafo do Terraform, permitindo que as rotas privadas sejam
criadas na mesma execução.

## Execução

Defina somente o `compartment_id`; os DRGs e suas rotas são criados no mesmo
`apply`:

```bash
terraform init
terraform fmt -check -recursive
terraform plan -var='compartment_id=<ocid>'
```
