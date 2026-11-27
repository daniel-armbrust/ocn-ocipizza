# Kubernetes da aplicação OCI Pizza

Este diretório contém os manifests Kubernetes e as customizações utilizadas
para implantar os serviços da aplicação nos clusters OKE de GRU e VCP.

## Organização do Kustomize

As definições comuns de cada microsserviço ficam em `base/`. As diferenças de
ambiente e região ficam em `overlays/`:

```text
kubernetes/
├── base/
│   ├── admin-service/
│   ├── chatbot-service/
│   ├── delivery-service/
│   ├── frontend-service/
│   ├── notification-service/
│   ├── order-service/
│   ├── pizza-service/
│   └── user-service/
└── overlays/
    ├── homol/
    │   ├── gru/
    │   └── vcp/
    └── prod/
        ├── gru/
        └── vcp/
```

Cada diretório regional possui um único `namespace.yaml` compartilhado pelos
serviços daquele ambiente no cluster. Seu `kustomization.yaml` funciona como
ponto de entrada e agrega o namespace e os overlays dos microsserviços. Cada
microsserviço mantém apenas suas customizações específicas no respectivo
subdiretório.

## Autenticação no OCI Container Registry

Todos os Deployments declaram `imagePullSecrets` na especificação do Pod e
referenciam um Secret chamado `ocir-secret`:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
        - name: ocir-secret
```

O Secret deve existir no mesmo namespace do Pod antes do deployment. Como os
namespaces `ocipizza-homol` e `ocipizza-prod` existem nos clusters de GRU e
VCP, são necessárias quatro instâncias do Secret. O conteúdo não faz parte dos
manifests versionados neste repositório.

Enquanto não houver integração com um gerenciador de Secrets, o recurso pode
ser criado operacionalmente com `kubectl`. No cluster de GRU, utilize o endpoint
regional `gru.ocir.io`:

```bash
kubectl create secret docker-registry ocir-secret \
  --namespace="ocipizza-homol" \
  --docker-server="gru.ocir.io" \
  --docker-username="$OCIR_USERNAME" \
  --docker-password="$OCIR_AUTH_TOKEN"
```

Repita o comando para `ocipizza-prod`. No cluster de VCP, selecione o contexto
correspondente, utilize os mesmos namespaces e altere o endpoint para
`vcp.ocir.io`. `OCIR_USERNAME` e `OCIR_AUTH_TOKEN` devem existir somente no
ambiente seguro do operador ou da pipeline e nunca devem ser gravados no Git.

## Configurações sensíveis do admin-service

O `admin-service` espera um Secret chamado `admin-service-secrets` no mesmo
namespace do Deployment. Esse Secret não faz parte dos manifests versionados e
deve ser provisionado pelo mecanismo seguro adotado na pipeline de deployment.

As seguintes chaves são obrigatórias:

- `redis-endpoint`: URI completa e autenticada do OCI Cache;
- `session-secret-key`: chave criptograficamente aleatória da sessão;
- `csrf-secret-key`: chave criptograficamente aleatória da proteção CSRF.

O mesmo nome de Secret é utilizado nos namespaces `ocipizza-homol` e
`ocipizza-prod`, mas cada namespace possui seu próprio recurso e seus próprios
valores.

O `frontend-service` segue a mesma separação e espera o Secret
`frontend-service-secrets`, também com as chaves `redis-endpoint`,
`session-secret-key` e `csrf-secret-key`. As chaves devem ser independentes das
utilizadas pelo `admin-service`.

O `user-service` espera dois recursos sensíveis provisionados fora do Git:

- `user-service-secrets`, contendo as chaves `database-write-url` e
  `database-read-url`;
- `user-service-jwt-public-key`, contendo `jwt_public_key.pem`.

A chave privada JWT não é montada no Pod. Ela é obtida em tempo de execução
do OCI Secret Management pelo OCID configurado em
`JWT_PRIVATE_KEY_SECRET_ID`.

## Scripts de Secrets

O diretório `scripts/` contém os scripts executados pelos Shell Stages das
Deployment Pipelines para materializar no Kubernetes os valores mantidos no
OCI Vault:

```text
scripts/
├── admin-service-secrets.sh
├── frontend-service-secrets.sh
├── user-service-secrets.sh
└── lib/
    └── secrets.sh
```

Os scripts exigem `ENVIRONMENT`, `REGION_KEY`, `KUBERNETES_NAMESPACE` e
`VAULT_ID`. Os scripts do `admin-service` e do `frontend-service` também
exigem `REDIS_HOST`; `REDIS_PORT` é opcional e usa `6379` por padrão. A
autenticação padrão da OCI CLI é `resource_principal`, adequada ao OCI
DevOps, e pode ser alterada por `OCI_AUTH_MODE`.

Os valores sensíveis são escritos somente em um diretório temporário com
permissão restrita, aplicado com `kubectl` e removido ao final da execução.
Nenhum manifesto contendo secrets é publicado no Git ou no Artifact Registry.
O namespace deve ser aplicado previamente pelo `namespace.yaml` do overlay;
os scripts apenas validam sua existência e não administram esse recurso.

O script do `user-service` lê o documento JSON
`ocipizza-user-service-database-credentials` do OCI Vault e monta as URLs sem
registrá-las nos logs. A URL de escrita utiliza
`mysql-write.ocipizza.internal`; a URL de leitura utiliza
`mysql-read.ocipizza.internal`.

Por exemplo, o manifesto completo de produção em GRU pode ser renderizado com:

```bash
kubectl kustomize kubernetes/overlays/prod/gru
```

Para inspecionar somente o `pizza-service`, utilize:

```bash
kubectl kustomize kubernetes/overlays/prod/gru/pizza-service
```

O comando apenas renderiza os manifests. Para aplicar o overlay regional no
cluster selecionado pelo contexto atual do `kubectl`, utilize:

```bash
kubectl apply -k kubernetes/overlays/prod/gru
```
