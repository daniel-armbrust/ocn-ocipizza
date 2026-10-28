# OKE Fundamentals

Exemplo Terraform de uma VCN para OKE na região `sa-saopaulo-1`, composta por:

- sub-rede pública para Load Balancers, com entrada TCP 80/443 permitida de `0.0.0.0/0`;
- sub-rede pública para o Kubernetes API Server, com a porta TCP 6443 restrita por `public_access_cidr`;
- sub-rede privada para worker nodes, com entrada e saída IPv4 abertas e saída externa por NAT Gateway;
- Service Gateway para acesso dos workers aos serviços da OCI.

O Terraform também reserva um endereço IPv4 público, cria a zona DNS pública
primária `ocipizza.com.br` e publica o endereço no registro A
`lb.ocipizza.com.br`. Após o provisionamento, consulte os outputs e configure
os nameservers retornados no registrador responsável pelo domínio:

```bash
terraform output dns_nameservers
terraform output load_balancer_public_ip
```

A reserva e o registro DNS não associam automaticamente o endereço ao Load
Balancer criado pelo Kubernetes. Ao criar o Service do tipo `LoadBalancer`,
configure-o para utilizar o endereço reservado exibido pelo output
`load_balancer_public_ip`.

As variáveis obrigatórias podem ser informadas diretamente na linha de comando.
Use o OCID da tenancy em `tenancy_id`, o OCID do compartment do laboratório em
`compartment_id` e o IP público autorizado como um host CIDR:

```bash
terraform plan \
  -var='tenancy_id=<ocid-da-tenancy>' \
  -var='compartment_id=<ocid>' \
  -var='public_access_cidr=203.0.113.10/32' \
  -var='cni_type=FLANNEL_OVERLAY' \
  -var='cluster_type=BASIC'

terraform apply \
  -var='tenancy_id=<ocid-da-tenancy>' \
  -var='compartment_id=<ocid>' \
  -var='public_access_cidr=203.0.113.10/32' \
  -var='cni_type=FLANNEL_OVERLAY' \
  -var='cluster_type=BASIC'
```

Para evitar repetir os valores em cada comando, utilize as variáveis de
ambiente reconhecidas automaticamente pelo Terraform:

```bash
export TF_VAR_tenancy_id='<ocid-da-tenancy>'
export TF_VAR_compartment_id='<ocid-do-compartment>'
export TF_VAR_public_access_cidr='203.0.113.10/32'

terraform plan \
  -var='cni_type=FLANNEL_OVERLAY' \
  -var='cluster_type=BASIC'

terraform apply \
  -var='cni_type=FLANNEL_OVERLAY' \
  -var='cluster_type=BASIC'
```

O OCID da tenancy normalmente está no campo `tenancy` do profile configurado
em `~/.oci/config`. Para obter o valor do primeiro profile presente no arquivo:

```bash
awk -F= '/^tenancy[[:space:]]*=/{gsub(/[[:space:]]/, "", $2); print $2; exit}' \
  "${OCI_CLI_CONFIG_FILE:-$HOME/.oci/config}"
```

Caso o arquivo possua vários profiles, confirme se o valor retornado pertence
ao mesmo profile indicado por `oci_config_profile`. Os valores de
`tenancy_id`, `compartment_id` e `public_access_cidr` não possuem padrão para
evitar que a infraestrutura seja criada no escopo errado ou exposta
acidentalmente.

## Acesso dos worker nodes ao OCIR

O Terraform cria diretamente no Root Compartment um Dynamic Group para as
Compute instances existentes no compartment do laboratório. Essa regra inclui
os worker nodes atuais e os substitutos criados posteriormente pelo node pool.
Uma policy concede ao grupo somente a permissão `read repos in tenancy`,
necessária para baixar imagens privadas do OCIR sem permitir publicação ou
exclusão.

Como a regra utiliza o OCID do compartment, outras Compute instances criadas
nesse mesmo compartment também pertencerão ao Dynamic Group. A variável
`tenancy_id` deve receber o OCID da tenancy, pois recursos IAM desse tipo são
obrigatoriamente criados no Root Compartment.

## Cluster OKE

O tipo padrão do cluster é `BASIC`, convertido internamente em
`BASIC_CLUSTER`. Também é possível usar `ENHANCED`, convertido em
`ENHANCED_CLUSTER`. A configuração pode ser informada por linha de comando ou
pela variável de ambiente do Terraform:

```bash
export TF_VAR_cluster_type='BASIC'
```

O CNI padrão é `OCI_VCN_IP_NATIVE`, nome utilizado pela API do OKE para o modo
VCN Native. Nesse modo, `pod_subnet_id` é obrigatório e identifica a sub-rede
usada pelos pods:

```bash
export TF_VAR_cni_type='OCI_VCN_IP_NATIVE'
export TF_VAR_pod_subnet_id='<ocid-da-sub-rede-dos-pods>'
```

Para utilizar Flannel, informe `FLANNEL_OVERLAY` explicitamente nos comandos
Terraform. Nesse modo, `pod_subnet_id` é opcional e não é enviado ao node
pool:

```bash
terraform plan \
  -var='cni_type=FLANNEL_OVERLAY' \
  -var='cluster_type=BASIC'

terraform apply \
  -var='cni_type=FLANNEL_OVERLAY' \
  -var='cluster_type=BASIC'
```

O Terraform reconhece variáveis de ambiente de entrada apenas com o prefixo
`TF_VAR_`; portanto, `CNI_TYPE`, `CLUSTER_TYPE` e `POD_SUBNET_ID` sem esse
prefixo não são consumidas automaticamente.

O node pool possui três workers x86 com as seguintes características:

- shape `VM.Standard.E4.Flex`;
- 2 OCPUs e 4 GB de memória por worker;
- sub-rede privada `worker_nodes`;
- imagem Oracle Linux x86 selecionada entre as opções compatíveis do OKE.

A versão padrão é `v1.34.10`, a versão estável mais antiga aceita para novos
clusters no momento da criação deste exemplo. Ela permite exercitar upgrades
sequenciais para as linhas 1.35 e 1.36. A OCI normalmente aceita apenas as três
versões minor mais recentes para novos clusters, podendo manter a quarta por
uma janela curta de transição. Por isso, uma versão quatro minors atrás não é
adequada para provisionamento reproduzível.

A versão pode ser alterada explicitamente durante o processo de upgrade:

```bash
terraform plan \
  -var='tenancy_id=<ocid-da-tenancy>' \
  -var='compartment_id=<ocid>' \
  -var='public_access_cidr=203.0.113.10/32' \
  -var='cni_type=FLANNEL_OVERLAY' \
  -var='cluster_type=BASIC' \
  -var='kubernetes_version=v1.35.2'
```

O control plane deve ser atualizado antes do node pool e os upgrades devem
respeitar as versões e caminhos suportados pelo OKE. Consulte a
[matriz de versões suportadas do OKE](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengaboutk8sversions.htm)
antes de iniciar cada etapa.

## Configuração do acesso com kubectl

Depois que a infraestrutura for criada com `terraform apply`, obtenha o OCID
do cluster pelo output do Terraform:

```bash
terraform output -raw oke_cluster_id
```

Em seguida, substitua `<OCID_DO_CLUSTER>` pelo valor retornado e gere o
kubeconfig utilizando o endpoint público do Kubernetes API Server:

```bash
oci ce cluster create-kubeconfig \
  --cluster-id <OCID_DO_CLUSTER> \
  --file ~/.kube/config \
  --region sa-saopaulo-1 \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT
```

O comando utiliza as credenciais configuradas no OCI CLI e adiciona o contexto
do cluster ao arquivo `~/.kube/config`. O IP público da máquina que executa o
comando deve estar autorizado pela variável `public_access_cidr`.

Valide o acesso ao cluster e aos worker nodes com:

```bash
kubectl cluster-info
kubectl get nodes
```

## Deploy dos Pods

O script `scripts/pods-deploy.sh` cria primeiro os namespaces definidos em
`kubernetes/namespaces/`. Em seguida, aplica os Pods de infraestrutura — Redis,
NoSQL, Object Storage, MySQL, RabbitMQ e Mailpit — antes dos Pods dos
microsserviços. O `envsubst` substitui `REGISTRY` e `OCI_NAMESPACE` nas
referências às imagens armazenadas no OCIR.

Os valores podem ser informados diretamente na linha de comando:

```bash
./scripts/pods-deploy.sh \
  --registry gru.ocir.io \
  --oci-namespace '<TENANCY_NAMESPACE>'
```

Também é possível defini-los por variáveis de ambiente:

```bash
export REGISTRY='gru.ocir.io'
export OCI_NAMESPACE="$(oci os ns get --query data --raw-output)"

./scripts/pods-deploy.sh
```

Os parâmetros `--registry` e `--oci-namespace` têm precedência sobre as
variáveis de ambiente. O script requer `kubectl`, `envsubst` e um contexto
Kubernetes configurado para acessar o cluster.

Para aplicar manualmente somente o Pod do `pizza-service`, primeiro crie o
namespace utilizado pelos serviços:

```bash
kubectl apply -f kubernetes/namespaces/ocipizza-services.yaml
```

Defina o endereço do OCIR e obtenha o namespace da tenancy. Em seguida,
processe o manifesto com `envsubst` e envie o resultado diretamente ao
`kubectl`:

```bash
export REGISTRY='gru.ocir.io'
export OCI_NAMESPACE="$(oci os ns get --query data --raw-output)"

envsubst '${REGISTRY} ${OCI_NAMESPACE}' \
  < kubernetes/pods/pod-pizza-service.yaml \
  | kubectl apply -f -
```

Verifique o estado, os eventos e os logs do Pod:

```bash
kubectl get pod pizza-service -n ocipizza-services
kubectl describe pod pizza-service -n ocipizza-services
kubectl logs pod/pizza-service -n ocipizza-services
```

Para excluir os Pods e depois remover os namespaces do laboratório, utilize os
mesmos valores usados no deploy:

```bash
./scripts/pods-delete.sh \
  --registry gru.ocir.io \
  --oci-namespace '<TENANCY_NAMESPACE>'
```

O script ignora recursos que já não existem. A remoção dos namespaces também
exclui qualquer recurso Kubernetes remanescente dentro deles.

### Bootstrap do pizza-service no OKE

O script `bootstrap/bootstrap-pizza-service.sh` reutiliza o bootstrap do
`pizza-service` para criar a tabela, cadastrar as pizzas de demonstração, criar
o bucket e enviar as imagens aos Pods de infraestrutura do cluster. Para isso,
ele abre temporariamente os seguintes forwards:

- `localhost:18080` para `pod/nosql:8080`;
- `localhost:9000` para `pod/objectstorage:9000`.

Execute o script depois que os Pods de infraestrutura estiverem disponíveis:

```bash
./bootstrap/bootstrap-pizza-service.sh
```

O script aguarda os Pods `nosql` e `objectstorage`, executa
`services/pizza-service/bootstrap.sh` com os endpoints locais e encerra os
processos de `kubectl port-forward` ao terminar ou receber uma interrupção.
As portas locais podem ser alteradas por `NOSQL_LOCAL_PORT` e
`OBJECTSTORAGE_LOCAL_PORT`.

## Construção e publicação de imagem no OCIR

O OCI Container Registry (OCIR) de São Paulo utiliza o domínio
`gru.ocir.io`. Antes de publicar uma imagem, obtenha estas informações:

- `<TENANCY_NAMESPACE>`: namespace de Object Storage da tenancy;
- `<USUARIO>`: usuário da OCI com permissão para publicar no repositório;
- `<REPOSITORIO>`: nome do repositório no OCIR, por exemplo
  `ocipizza/pizza-service`;
- `<VERSAO>`: versão imutável da imagem, por exemplo `1.0.0`.

O repositório deve existir no OCIR, salvo quando as políticas da tenancy
permitirem sua criação automática durante o primeiro push. O usuário também
precisa de um Auth Token da OCI; a senha da Console não deve ser utilizada.

### 1. Construir a imagem

Os worker nodes deste laboratório usam o shape x86 `VM.Standard.E4.Flex`.
Portanto, a imagem deve ser construída para `linux/amd64`:

```bash
docker build \
  --platform linux/amd64 \
  --tag pizza-service:1.0.0 \
  <CAMINHO_DO_CONTEXTO>
```

`<CAMINHO_DO_CONTEXTO>` é o diretório que contém o `Dockerfile` e os arquivos
necessários para o build.

Por exemplo, para construir o `pizza-service` a partir da raiz do repositório:

```bash
cd ~/ocn-ocipizza/
cd services/pizza-service/
docker build --platform linux/amd64 --tag pizza-service:1.0.0 .
```

Nesse exemplo, o ponto (`.`) define `services/pizza-service/` como o contexto
do build e o Docker utiliza o `Dockerfile` existente nesse diretório.

### 2. Autenticar no OCIR

Consulte o namespace de Object Storage da tenancy com o OCI CLI:

```bash
oci os ns get
```

O resultado possui o namespace no campo `data`:

```json
{
  "data": "<TENANCY_NAMESPACE>"
}
```

Para retornar somente o valor, sem a estrutura JSON, execute:

```bash
oci os ns get --query data --raw-output
```

Execute o login informando o usuário no formato
`<TENANCY_NAMESPACE>/<USUARIO>`:

```bash
docker login gru.ocir.io \
  --username '<TENANCY_NAMESPACE>/<USUARIO>'
```

Quando o Docker solicitar a senha, informe o Auth Token. Não coloque o token
diretamente no comando nem o armazene no repositório.

Para usuários de um IAM Identity Domain diferente do domínio padrão, utilize:

```text
<TENANCY_NAMESPACE>/<IDENTITY_DOMAIN>/<USUARIO>
```

### 3. Aplicar a tag do OCIR

O nome completo exigido pelo OCIR segue o formato:

```text
gru.ocir.io/<TENANCY_NAMESPACE>/<REPOSITORIO>:<VERSAO>
```

Aplique essa tag à imagem local:

```bash
docker tag pizza-service:1.0.0 \
  gru.ocir.io/<TENANCY_NAMESPACE>/ocipizza/pizza-service:1.0.0
```

### 4. Enviar a imagem

Envie a imagem para o repositório:

```bash
docker push \
  gru.ocir.io/<TENANCY_NAMESPACE>/ocipizza/pizza-service:1.0.0
```

O mesmo nome completo deve ser utilizado no campo `image` dos manifests do
Kubernetes. Evite reutilizar tags em ambientes controlados; prefira uma nova
versão para cada build.

Consulte também a documentação oficial sobre
[publicação de imagens com Docker no OCIR](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrypushingimagesusingthedockercli.htm).

## Build e push automatizados

O script [`scripts/images-build-push.sh`](../scripts/images-build-push.sh)
executa o build, aplica as tags do OCIR e publica todos os serviços que possuem
`Dockerfile` em `services/`. Execute-o a partir da raiz do repositório:

```bash
./scripts/images-build-push.sh \
  --user '<USUARIO>' \
  --tag 1.0.0
```

Para reconstruir todas as camadas sem utilizar o cache do Docker:

```bash
./scripts/images-build-push.sh \
  --user '<USUARIO>' \
  --tag 1.0.0 \
  --no-cache
```

O namespace é obtido automaticamente com `oci os ns get`. O prefixo padrão
dos repositórios é `ocipizza` e pode ser alterado com
`--repository-prefix <prefixo>`.

Antes de executar `docker login`, o script verifica o arquivo
`${DOCKER_CONFIG:-$HOME/.docker}/config.json`. Quando já existe uma credencial
para `gru.ocir.io`, a autenticação armazenada é reutilizada e o Auth Token não
é solicitado novamente. Sem uma credencial existente, o login continua sendo
feito de forma interativa.

Para executar somente a exclusão das imagens, dos respectivos repositórios no
OCIR e das imagens no Docker local, utilize `--remove`:

```bash
./scripts/images-build-push.sh \
  --tag 1.0.0 \
  --remove
```

Essa opção é destrutiva e não executa build, tag, login do Docker ou push. O
script localiza cada imagem pela combinação repositório/versão, exclui o
recurso remoto e consulta o repositório no Root Compartment usando o OCID da
tenancy. Em seguida, exclui o repositório sem confirmação adicional e remove
as referências local e completa do cache da máquina. O parâmetro `--user` não
é necessário nesse modo, pois a exclusão utiliza as credenciais configuradas
no OCI CLI.

O OCID do Root Compartment é o próprio OCID da tenancy. O script utiliza
primeiro `OCI_CLI_TENANCY`, quando essa variável estiver definida. Caso
contrário, lê o campo `tenancy` do profile indicado por `OCI_CLI_PROFILE` no
arquivo `${OCI_CLI_CONFIG_FILE:-$HOME/.oci/config}`. O profile padrão é
`DEFAULT`. Mesmo quando a imagem ou versão já tiver sido removida, o script
ainda procura e exclui o repositório vazio correspondente.

Atualmente, a remoção considera que os repositórios `ocipizza/<serviço>` são
exclusivos das imagens da aplicação. 

Existe um `TODO` no script para que uma versão futura verifique outros artefatos OCI, como Helm charts, antes de excluir o repositório.
