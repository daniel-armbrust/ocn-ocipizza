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
Uma policy concede ao grupo a leitura de imagens nos repositórios
`ocipizza/*`. Para o pull de imagens privadas pelos Pods, ainda é necessário
configurar um Secret `docker-registry` no namespace Kubernetes.

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

## Acesso às imagens privadas do OCIR

O acesso às imagens privadas utiliza dois controles complementares: a policy
IAM autoriza os worker nodes e o Secret `docker-registry` fornece ao runtime do
Kubernetes as credenciais utilizadas no pull das imagens.

O Terraform deste laboratório cria no Root Compartment o Dynamic Group dos
worker nodes e a policy com a seguinte instrução:

```text
Allow dynamic-group id <OCID_DO_DYNAMIC_GROUP> to read repos in tenancy where all { target.repo.name=/ocipizza\/*/ }
```

A condição `target.repo.name=/ocipizza\/*/` permite a leitura somente das
imagens existentes em repositórios cujos nomes estejam abaixo de `ocipizza/`,
como `ocipizza/pizza-service` e `ocipizza/user-service`. Ela não permite ler
repositórios como `outro/pizza-service` ou `ocipizza-teste/pizza-service` e o
verbo `read` não concede permissão para publicar ou excluir imagens.

Os Secrets do Kubernetes são limitados ao namespace. Portanto, o script
`kubernetes/secrets/ocir-service-account-setup.sh` cria o mesmo Secret em cada
namespace que executará Pods com imagens privadas, associa-o ao
`ServiceAccount` padrão e solicita o Auth Token sem exibi-lo:

```bash
./kubernetes/secrets/ocir-service-account-setup.sh \
  --registry gru.ocir.io \
  --oci-namespace "$(oci os ns get --query data --raw-output)" \
  --user '<USUARIO_OCI>'
```

O namespace da tenancy também é obtido automaticamente pelo comando
`oci os ns get` quando `--oci-namespace` e `OCI_NAMESPACE` não são informados.
As opções podem ser substituídas pelas variáveis de ambiente `REGISTRY`,
`OCI_NAMESPACE` e `OCI_USERNAME`. Para execução não interativa, o Auth Token
pode ser fornecido por `OCI_AUTH_TOKEN` somente no ambiente do processo.

Exemplo utilizando as variáveis de ambiente:

```bash
export REGISTRY='gru.ocir.io'
export OCI_NAMESPACE="$(oci os ns get --query data --raw-output)"
export OCI_USERNAME='<USUARIO_OCI>'
export OCI_AUTH_TOKEN='<AUTH_TOKEN_OCI>'

./kubernetes/secrets/ocir-service-account-setup.sh
```

### Comandos equivalentes com kubectl

Para executar manualmente a criação ou atualização do `ocir-secret`, utilize
as mesmas variáveis de ambiente e aplique o Secret nos dois namespaces:

```bash
for kubernetes_namespace in ocipizza-infra ocipizza-services; do
  kubectl create secret docker-registry ocir-secret \
    --namespace "${kubernetes_namespace}" \
    --docker-server "${REGISTRY}" \
    --docker-username "${OCI_NAMESPACE}/${OCI_USERNAME}" \
    --docker-password "${OCI_AUTH_TOKEN}" \
    --dry-run=client \
    --output yaml \
    | kubectl apply -f -
done
```

Para disponibilizar esse Secret automaticamente a todos os Pods que utilizam
o `ServiceAccount default`, associe-o em cada namespace:

```bash
for kubernetes_namespace in ocipizza-infra ocipizza-services; do
  kubectl patch serviceaccount default \
    --namespace "${kubernetes_namespace}" \
    --type strategic \
    --patch '{"imagePullSecrets":[{"name":"ocir-secret"}]}'
done
```

Sem a associação ao `ServiceAccount`, mantenha somente o primeiro comando e
adicione `imagePullSecrets` diretamente ao manifesto do Pod ou ao seu template,
conforme o exemplo YAML apresentado a seguir.

Para conferir o Secret e a configuração do `ServiceAccount`:

```bash
kubectl get secret ocir-secret --namespace ocipizza-services
kubectl get serviceaccount default \
  --namespace ocipizza-services \
  --output yaml
```

Para excluir manualmente o Secret dos dois namespaces:

```bash
for kubernetes_namespace in ocipizza-infra ocipizza-services; do
  kubectl delete secret ocir-secret \
    --namespace "${kubernetes_namespace}" \
    --ignore-not-found
done
```

Esse último comando não remove a referência existente no `ServiceAccount`.
Para remover de forma segura tanto a referência quanto o Secret, preservando
outros `imagePullSecrets`, utilize o script de remoção documentado a seguir.

Ao associar o Secret ao `ServiceAccount` padrão, os Pods desses namespaces
herdam `imagePullSecrets` sem que essa configuração precise ser repetida em
cada manifesto. O Auth Token é um dado sensível e não deve ser armazenado no
repositório.

Como alternativa, o script `kubernetes/secrets/ocir-image-pull-secret-setup.sh`
somente cria ou atualiza o `ocir-secret`, sem modificar o `ServiceAccount`:

```bash
./kubernetes/secrets/ocir-image-pull-secret-setup.sh
```

Nesse modo, cada Pod ou template de Pod que utiliza uma imagem privada deve
referenciar explicitamente o Secret no mesmo namespace:

```yaml
spec:
  imagePullSecrets:
    - name: ocir-secret
  containers:
    # Configuração dos containers do Pod.
```

Para remover o `ocir-secret` criado por qualquer uma das abordagens, execute:

```bash
./kubernetes/secrets/ocir-image-pull-secret-remove.sh
```

O script remove a referência a `ocir-secret` do `ServiceAccount default`, sem
afetar outros `imagePullSecrets`, e exclui o Secret dos namespaces
`ocipizza-infra` e `ocipizza-services`. O `ServiceAccount default` não é
excluído porque ele é gerenciado automaticamente pelo Kubernetes.

## Makefile do laboratório

O arquivo `oke-fundamentals/Makefile` reúne os comandos mais comuns para
preparar, implantar, consultar e remover o laboratório. Execute os comandos a
partir do diretório `oke-fundamentals`:

```bash
cd oke-fundamentals
make help
```

Para executar `make image-pull-secret` ou o fluxo completo, defina as
variáveis utilizadas pelo OCIR. `OCI_AUTH_TOKEN` pode ser omitida quando o
script puder solicitá-la de forma interativa:

```bash
export REGISTRY='gru.ocir.io'
export OCI_NAMESPACE="$(oci os ns get --query data --raw-output)"
export OCI_USERNAME='<USUARIO_OCI>'
export OCI_AUTH_TOKEN='<AUTH_TOKEN_OCI>'

make ocipizza
```

O Auth Token não deve ser armazenado no repositório nem incluído em arquivos
versionados.

Os principais alvos são:

- `make namespace`: cria os namespaces `ocipizza-infra` e
  `ocipizza-services`;
- `make image-pull-secret`: cria ou atualiza o Secret `ocir-secret`;
- `make pvc`: cria os PVCs definidos para os serviços de infraestrutura;
- `make infra`: chama o `deploy.sh` de cada serviço de infraestrutura, na
  ordem MySQL, NoSQL, RabbitMQ, Redis, ObjectStorage e Mailpit. Os PVCs devem
  ser criados previamente com `make pvc`;
- `make bootstrap`: executa os scripts de bootstrap dos microsserviços;
- `make services`: aplica os Deployments e Services dos microsserviços;
- `make status`: exibe Deployments, Pods, Services, PVCs e Secrets do projeto;
- `make ocipizza`: executa o fluxo completo na ordem namespace,
  image-pull-secret, PVCs, infraestrutura, bootstrap, microsserviços e, por
  último, o OCI Native Ingress Controller standalone;
- `make delete-ocipizza`: remove primeiro o OCI Native Ingress Controller,
  depois microsserviços, infraestrutura, PVCs, Secret do OCIR e namespaces.

O alvo `make infra` utiliza os scripts abaixo, mantendo a lógica de cada
serviço junto aos seus manifestos:

```text
kubernetes/infra/mysql/deploy.sh
kubernetes/infra/nosql/deploy.sh
kubernetes/infra/rabbitmq/deploy.sh
kubernetes/infra/redis/deploy.sh
kubernetes/infra/objectstorage/deploy.sh
kubernetes/infra/mailpit/deploy.sh
```

O alvo `make delete-infra` executa os respectivos `undeploy.sh` na mesma ordem
e remove os PVCs depois que os Deployments e Services forem excluídos. Os
scripts verificam os manifestos, exigem `kubectl` no `PATH` e usam
`--ignore-not-found` durante a remoção.

## Ingress e Load Balancer

O `ingress-nginx` utiliza um único Service do tipo `LoadBalancer`, definido em
`kubernetes/ingress-nginx/service.yaml`. Consequentemente, um único Load
Balancer OCI atende os hosts configurados em
`kubernetes/ingress-nginx/ingress.yaml`.

Os registros DNS abaixo devem apontar para o endereço do mesmo Load Balancer:

```text
www.ocipizza.com.br
mailpit.ocipizza.com.br
rabbitmq.ocipizza.com.br
objectstorage.ocipizza.com.br
```

O manifesto de Ingress encaminha as requisições da seguinte forma:

```text
www.ocipizza.com.br       → admin-service ou frontend-service
mailpit.ocipizza.com.br   → mailpit:8025
rabbitmq.ocipizza.com.br  → rabbitmq:15672
objectstorage.ocipizza.com.br → objectstorage:9001
```

Os hosts de infraestrutura são definidos no namespace `ocipizza-infra`, e os
hosts da aplicação no namespace `ocipizza-services`. O controlador continua
centralizado no namespace `ingress-nginx`.

Para instalar ou excluir o controlador e suas regras:

```bash
make ingress-nginx
make delete-ingress-nginx
```

O OCI Native Ingress Controller pode ser instalado no modo standalone com
Helm. Esse fluxo também aplica os recursos `IngressClassParameters`,
`IngressClass` e `Ingress` do diretório
`kubernetes/oci-native-ingress/`:

```bash
export OKE_CLUSTER_ID='<OCID_DO_CLUSTER>'
export OKE_LOAD_BALANCER_COMPARTMENT_ID='<OCID_DO_COMPARTMENT_DO_LB>'
export OKE_LOAD_BALANCER_SUBNET_ID='<OCID_DA_SUBREDE_DO_LB>'

make oci-native-ingress
make delete-oci-native-ingress
```

O `IngressClassParameters.yaml` é renderizado pelo script com `envsubst`
antes de ser aplicado. O Load Balancer criado pelo OCI Native Ingress
Controller é independente do Service `LoadBalancer` usado pelo
`ingress-nginx`.

No OCI Native Ingress, os Ingresses da aplicação e da infraestrutura utilizam
um único listener HTTP público na porta `80`, configurado pela annotation:

```yaml
oci-native-ingress.oraclecloud.com/http-listener-port: "80"
```

O Load Balancer não cria listeners separados para as portas dos Services. O
roteamento é realizado pelo host e pelo caminho recebido:

```text
www.ocipizza.com.br                  → frontend-service:8000
www.ocipizza.com.br/admin            → admin-service:8000
www.ocipizza.com.br/kitchen          → admin-service:8000
mailpit.ocipizza.com.br              → mailpit:8025
rabbitmq.ocipizza.com.br             → rabbitmq:15672
objectstorage.ocipizza.com.br        → objectstorage:9001
```

Os Services usados como backend pelo OCI Native Ingress devem utilizar o tipo
`NodePort`. Services que não possuem uma regra de Ingress podem continuar como
`ClusterIP`.

As interfaces administrativas de infraestrutura devem ser protegidas por
regras de rede, autenticação e/ou restrição ao IP de administração antes de
serem expostas fora do ambiente de laboratório.

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

O script `kubernetes/ocipizza/pizza-service/bootstrap.sh` reutiliza o bootstrap
do `pizza-service` para criar a tabela, cadastrar as pizzas de demonstração,
criar o bucket e enviar as imagens aos Pods de infraestrutura do cluster. Para
isso, ele abre temporariamente os seguintes forwards:

- `localhost:18080` para `pod/nosql:8080`;
- `localhost:9000` para `pod/objectstorage:9000`.

Execute o script depois que os Pods de infraestrutura estiverem disponíveis:

```bash
./kubernetes/ocipizza/pizza-service/bootstrap.sh
```

O script aguarda os Pods `nosql` e `objectstorage`, executa
`services/pizza-service/bootstrap.sh` com os endpoints locais e encerra os
processos de `kubectl port-forward` ao terminar ou receber uma interrupção.

### Bootstrap do user-service no OKE

O script `kubernetes/ocipizza/user-service/bootstrap.sh` reutiliza o bootstrap
original do `user-service` para aplicar as migrations e cadastrar os usuários
de demonstração no MySQL do cluster. Durante a execução, ele encaminha
temporariamente `localhost:13306` para a porta 3306 do Pod identificado pelo
label `app=mysql`. Dessa forma, o bootstrap funciona com um Pod criado
diretamente, por ReplicationController ou por ReplicaSet.

Depois do bootstrap, o script cria ou atualiza o Secret `user-service-jwt` no
namespace `ocipizza-services`, contendo as seguintes chaves:

- `jwt_private_key.pem`;
- `jwt_public_key.pem`.

Execute o script depois que o Pod do MySQL estiver disponível:

```bash
./kubernetes/ocipizza/user-service/bootstrap.sh
```

As chaves são obtidas de `services/user-service/secrets/`. Caso ainda não
existam, o bootstrap original gera um novo par RSA antes da criação do Secret.
O bootstrap original define `OCI_REGION` como `sa-saopaulo-1` por padrão; o
valor pode ser sobrescrito por uma variável de ambiente de mesmo nome.
O processo de `kubectl port-forward` é encerrado automaticamente ao término ou
quando o script recebe uma interrupção.
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

Para processar somente um serviço, informe o nome do diretório do serviço ao
final do comando. Sem esse argumento, todos os serviços com `Dockerfile` são
processados:

```bash
./scripts/images-build-push.sh \
  --user '<USUARIO>' \
  --tag 1.0.0 \
  --no-cache \
  pizza-service
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
