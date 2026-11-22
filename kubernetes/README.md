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

- `user-service-secrets`, contendo a chave `database-url`;
- `user-service-jwt-public-key`, contendo `jwt_public_key.pem`.

A chave privada JWT não é montada no Pod. Ela é obtida em tempo de execução
do OCI Secret Management pelo OCID configurado em
`JWT_PRIVATE_KEY_SECRET_ID`.

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
