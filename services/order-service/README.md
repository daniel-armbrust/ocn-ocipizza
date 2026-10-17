# OCI Pizza — Order Service: criação e acompanhamento de pedidos

## Responsabilidade do Serviço

O `order-service` é responsável por registrar e consultar os pedidos da OCI
Pizza depois que os dados do checkout e o pagamento foram confirmados.

Suas principais responsabilidades são:

- Criar pedidos vinculados ao usuário autenticado
- Preservar snapshots do cliente, endereço, pizzas e valores da compra
- Impedir pedidos duplicados por meio de uma chave de idempotência
- Listar e consultar os pedidos do próprio usuário
- Disponibilizar o acompanhamento administrativo de todos os pedidos
- Atualizar administrativamente o status de processamento e entrega
- Publicar solicitações de notificação após a criação do pedido
- Persistir pedidos e seus estados no Oracle NoSQL
- Validar access tokens JWT por meio do JWKS publicado pelo `user-service`
- Expor respostas HTTP no padrão JSend

O serviço não consulta novamente usuários, endereços, pizzas ou cotações de
entrega durante a criação. Essas informações chegam como snapshots já
confirmados pelo fluxo de checkout e permanecem preservadas no pedido mesmo
que os dados originais sejam modificados posteriormente.

## Dependências do Serviço

| Componente | Responsabilidade |
| --- | --- |
| Oracle NoSQL | Provider primário e atualmente implementado para persistência dos pedidos. |
| `user-service` | Publica o JWKS utilizado para validar access tokens JWT. |
| RabbitMQ ou OCI Queue | Publica mensagens destinadas ao `notification-service`. |

O Oracle NoSQL é o provider padrão. O projeto contém a estrutura básica para
SQLAlchemy, mas o repositório relacional de pedidos não está disponível para
as operações da API e o bootstrap aceita somente
`PERSISTENCE_PROVIDER=nosql`.

### Dependências Python

As bibliotecas são instaladas a partir do arquivo `requirements.txt`:

| Biblioteca | Versão | Uso principal |
| --- | --- | --- |
| FastAPI | 0.141.1 | Implementação da API REST e injeção de dependências. |
| pydantic-settings | 2.10.1 | Leitura e validação das configurações de ambiente. |
| HTTPX | 0.28.1 | Consulta assíncrona ao JWKS publicado pelo `user-service`. |
| SQLAlchemy | 2.0.43 | Estrutura do provider relacional alternativo. |
| Alembic | 1.16.5 | Versionamento previsto para o schema relacional. |
| PyMySQL | 1.1.2 | Driver previsto para uma conexão MySQL. |
| PyJWT com extra `crypto` | `>=2.10,<3` | Validação de access tokens JWT assinados com RS256. |
| pika | 1.3.2 | Publicação de mensagens no RabbitMQ. |
| OCI SDK | 2.160.3 | Integração com OCI Queue e OCI Logging. |
| borneo | 5.4.3 | Acesso ao Oracle NoSQL Database. |

O ambiente de execução utiliza Python 3.11.

## `bootstrap.sh` — Bootstrap do ambiente local

O script `bootstrap.sh` prepara o ambiente Python, cria a configuração local e
recria a tabela e os índices utilizados pelo serviço no Oracle NoSQL.

> **Atenção:** o bootstrap é destrutivo e deve ser utilizado somente para
> preparar o ambiente de desenvolvimento. Ele executa `DROP TABLE IF EXISTS`
> antes de recriar a tabela `orders`; portanto, todos os pedidos existentes na
> tabela configurada serão removidos.

### Pré-requisitos

- Python 3.11
- Oracle NoSQL local disponível na porta `18080`

Para iniciar a infraestrutura a partir da raiz do monorepo:

```bash
make development-infra
```

Ou inicie somente o Oracle NoSQL:

```bash
docker compose up -d nosql
docker compose ps nosql
```

### Execução

A partir da raiz do monorepo:

```bash
cd services/order-service
./bootstrap.sh
```

Caso o script não possua permissão de execução:

```bash
bash bootstrap.sh
```

A execução foi concluída corretamente quando o terminal exibir:

```text
Bootstrap do order-service concluído com sucesso
```

Depois do bootstrap, volte à raiz do monorepo e inicie o serviço:

```bash
cd ../..
docker compose up -d order-service
docker compose ps order-service
```

### O que o bootstrap executa

1. Valida a disponibilidade do Python 3.11
2. Cria e ativa o ambiente virtual `.venv`
3. Atualiza o `pip` e instala o `requirements.txt`
4. Cria o arquivo `.env`, caso ele ainda não exista
5. Carrega as configurações locais
6. Valida o provider definido em `PERSISTENCE_PROVIDER`
7. Exclui a tabela `orders`, caso ela exista
8. Recria a tabela e os índices utilizados nas consultas e ordenações

### Configuração local criada

O `.env` criado pelo bootstrap utiliza:

- `APP_NAME=order-service`
- `APP_ENV=development`
- `PERSISTENCE_PROVIDER=nosql`
- Tabela `orders`
- Oracle NoSQL em `http://localhost:18080`
- Mensageria com RabbitMQ
- Fila `notifications-queue`
- Emissor JWT `user-service`
- Audiência JWT `ocipizza`
- JWKS em `http://localhost:8002/.well-known/jwks.json`
- Logging com nível `INFO`

Se o `.env` já existir, seus valores serão preservados. Configurações locais
obrigatórias de mensageria que ainda não existirem serão acrescentadas pelo
bootstrap sem sobrescrever as definições existentes.

## Reconstruir a imagem Docker

Após modificar o serviço, reconstrua sua imagem a partir da raiz do monorepo:

```bash
docker compose build --no-cache order-service
docker compose up -d order-service
docker compose ps order-service
```

O container executa a aplicação com um usuário não privilegiado e publica
internamente a porta `8000`. No ambiente local do Docker Compose, ela é
exposta como `8004`.

## Persistência

### Oracle NoSQL

O provider `nosql` utiliza a tabela definida por `NOSQL_TABLE_NAME`. Em
desenvolvimento, `NOSQL_ENDPOINT` é obrigatório e aponta para o Oracle NoSQL
local.

Fora de `development`, cada instância do serviço acessa o Oracle NoSQL da
região OCI em que está sendo executada. A autenticação utiliza Instance
Principal e `OCI_REGION` é obrigatória para selecionar a região.

A tabela `orders` contém os campos:

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id` | string/UUID | Identificador único do pedido. |
| `user_id` | string/UUID | Identificador do proprietário do pedido. |
| `customer` | record | Snapshot do nome, e-mail e WhatsApp do cliente. |
| `delivery_address` | record | Snapshot completo do endereço de entrega. |
| `items` | array de records | Pizzas, quantidades, preços unitários e subtotais confirmados. |
| `subtotal` | number | Soma dos subtotais dos itens. |
| `delivery_fee` | number | Taxa de entrega confirmada. |
| `total` | number | Soma do subtotal com a taxa de entrega. |
| `status` | string | Estado de processamento e entrega do pedido. |
| `payment_status` | string | Estado do pagamento. |
| `idempotency_key` | string/UUID | Chave da tentativa de criação. |
| `created_at` | timestamp | Data e hora de criação em UTC. |
| `updated_at` | timestamp | Data e hora da última atualização em UTC. |

O bootstrap cria índices para:

- Pedidos por usuário e data de criação
- Chave de idempotência
- Status do pedido
- Status do pagamento
- Combinação dos dois status com ordenação por data

### Unidade de trabalho

As regras de negócio dependem da abstração `UnitOfWork`. No Oracle NoSQL, a
implementação é `NosqlNoOpUnitOfWork`, pois cada operação utilizada pelo
serviço é confirmada pelo próprio banco e não possui `commit` transacional
equivalente ao SQLAlchemy. A camada de serviço continua chamando `commit()` e
`rollback()` sem conhecer o provider configurado.

## Mensageria e notificações

Depois de persistir e confirmar a criação de um pedido, o serviço publica uma
solicitação de notificação na fila configurada. A mensagem utiliza o tipo
`ORDER_RECEIVED` e contém:

- E-mail e nome do cliente
- Identificador do pedido
- Itens, quantidades, preços unitários e totais
- Subtotal, taxa de entrega e total

Exemplo do contrato publicado:

```json
{
  "type": "ORDER_RECEIVED",
  "recipient": "ana.laura@example.com",
  "full_name": "Ana Laura",
  "order_id": "93da1548-90ba-4b69-83e2-dfe4d42bcdb4",
  "items": [
    {
      "name": "Margherita",
      "quantity": 2,
      "unit_price": "45.00",
      "total": "90.00"
    }
  ],
  "subtotal": "90.00",
  "delivery_fee": "10.00",
  "total": "100.00"
}
```

Os campos monetários `unit_price`, `items[].total`, `subtotal`,
`delivery_fee` e `total` são serializados como strings decimais com exatamente
duas casas. Esse formato evita perda de precisão no JSON e impede que valores
como `Decimal('1E+1')` sejam apresentados em notação científica no e-mail.

A publicação ocorre somente depois do `commit` do pedido. Se ela falhar, o
erro é registrado, mas o pedido permanece criado e a API continua retornando o
pedido com sucesso. Não existe outbox nem nova tentativa automática no
`order-service`. Requisições idempotentes que retornam um pedido criado por uma
requisição concorrente não publicam uma segunda mensagem.

Após a atualização administrativa do status, o serviço publica uma notificação
específica para `OUT_FOR_DELIVERY` (`ORDER_SENT`) e `DELIVERED`
(`ORDER_DELIVERED`). Os demais estados utilizam `ORDER_UPDATED`.

### RabbitMQ

Com `MESSAGING_PROVIDER=rabbitmq`, o publicador declara `QUEUE_NAME` como fila
durável, publica JSON persistente pelo exchange padrão e aguarda a confirmação
do broker. Host, porta, usuário e senha são obrigatórios.

### OCI Queue

Com `MESSAGING_PROVIDER=oci_queue`, o publicador envia o JSON ao
`OCI_QUEUE_MESSAGES_ENDPOINT` da fila identificada por `OCI_QUEUE_ID`. A
autenticação utiliza Instance Principal; a instância deve pertencer a um
Dynamic Group autorizado por uma IAM Policy a publicar mensagens na fila.

O endpoint configurado deve ser o `messagesEndpoint` específico da fila, e não
o endpoint administrativo do serviço OCI Queue.

<!-- TODO: Implementar um mecanismo transacional de outbox ou retry persistente
para evitar a perda da notificação quando a fila estiver indisponível depois do
commit do pedido. -->

## Logging

O logging é configurado durante a inicialização da aplicação:

- Os logs são sempre enviados para `stdout`
- Fora de `development`, eles também são enviados ao OCI Logging pela Logging
  Ingestion API
- A autenticação no OCI Logging utiliza Instance Principal
- Fora de `development`, `OCI_LOG_ID` é obrigatório
- Exceções inesperadas e falhas internas de criação, consulta ou atualização
  são registradas antes da resposta HTTP 500

## Como utilizar a API de pedidos

O serviço fica disponível localmente em:

```text
http://localhost:8004
```

As respostas seguem o padrão JSend.

### Rotas disponíveis

| Operação | Método HTTP | Endpoint | Acesso |
| --- | --- | --- | --- |
| Criar pedido | `POST` | `/orders` | Usuário autenticado. |
| Listar meus pedidos | `GET` | `/orders` | Usuário autenticado. |
| Consultar meu pedido | `GET` | `/orders/{order_id}` | Proprietário autenticado. |
| Listar todos os pedidos | `GET` | `/admin/orders` | Admin ou cozinha autenticados. |
| Resumir indicadores dos pedidos | `GET` | `/admin/orders/summary` | Admin ou cozinha autenticados. |
| Consultar qualquer pedido | `GET` | `/admin/orders/{order_id}` | Admin ou cozinha autenticados. |
| Atualizar status do pedido | `PATCH` | `/admin/orders/{order_id}/status` | Admin ou cozinha autenticados. |
| Excluir pedido | `DELETE` | `/admin/orders/{order_id}` | Administrador autenticado. |
| Health check | `GET` | `/health` | Público. |

## Autenticação e autorização

Todas as rotas de pedidos exigem um access token JWT no cabeçalho:

```http
Authorization: Bearer <access_token>
```

O token é validado com a chave pública correspondente ao `kid`, obtida no JWKS
do `user-service`. A validação verifica:

- Assinatura RS256
- Emissor definido em `JWT_ISSUER`
- Audiência definida em `JWT_AUDIENCE`
- Prazo de validade do token
- Claim `sub` contendo um UUID de usuário válido

As rotas de consulta e atualização sob `/admin/orders` aceitam um dos seguintes
claims:

```json
{
  "is_admin": true
}
```

Usuários com `is_kitchen: true` também podem consultar pedidos e atualizar seus
status. A exclusão em `DELETE /admin/orders/{order_id}` exige exclusivamente
`is_admin: true`.

O serviço não utiliza uma claim `role` para decidir a autorização.

O serviço tenta aquecer o cache de chaves públicas durante a inicialização.
Quando o `kid` solicitado não está no cache, o JWKS é consultado novamente.

## Operações do usuário

### POST `/orders` — Criar pedido

O `user_id` não é aceito no corpo. Ele é obtido do claim `sub` do access token
para impedir a criação de pedidos em nome de outro usuário.

Exemplo:

```bash
curl --request POST \
  --url http://localhost:8004/orders \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "customer": {
      "name": "Ana Laura",
      "email": "ana.laura@example.com",
      "whatsapp": "11966666666"
    },
    "delivery_address": {
      "zip_code": "18040425",
      "street": "Rua Exemplo",
      "number": "123",
      "complement": null,
      "neighborhood": "Campolim",
      "city": "Sorocaba",
      "state": "SP"
    },
    "items": [
      {
        "pizza_id": "8cfd7fa7-607d-4655-bd54-11edc2d07af8",
        "name": "Calabresa",
        "quantity": 2,
        "unit_price": "45.00",
        "subtotal": "90.00"
      }
    ],
    "subtotal": "90.00",
    "delivery_fee": "8.50",
    "total": "98.50",
    "idempotency_key": "93da1548-90ba-4b69-83e2-dfe4d42bcdb4"
  }'
```

Resposta `201 Created`:

```json
{
  "status": "success",
  "data": {
    "order": {
      "id": "e8f11694-e824-5fc4-8517-593055634935",
      "user_id": "ca54bc39-0c1f-433f-9349-3fd720d5757d",
      "customer": {
        "name": "Ana Laura",
        "email": "ana.laura@example.com",
        "whatsapp": "11966666666"
      },
      "delivery_address": {
        "zip_code": "18040425",
        "street": "Rua Exemplo",
        "number": "123",
        "complement": null,
        "neighborhood": "Campolim",
        "city": "Sorocaba",
        "state": "SP"
      },
      "items": [
        {
          "pizza_id": "8cfd7fa7-607d-4655-bd54-11edc2d07af8",
          "name": "Calabresa",
          "quantity": 2,
          "unit_price": "45.00",
          "subtotal": "90.00"
        }
      ],
      "subtotal": "90.00",
      "delivery_fee": "8.50",
      "total": "98.50",
      "status": "RECEIVED",
      "payment_status": "PAID",
      "idempotency_key": "93da1548-90ba-4b69-83e2-dfe4d42bcdb4",
      "created_at": "2026-10-12T15:00:00Z",
      "updated_at": "2026-10-12T15:00:00Z"
    }
  }
}
```

O pedido nasce com `status=RECEIVED` e `payment_status=PAID`. No fluxo atual de
desenvolvimento, o frontend ainda utiliza um token de pagamento fictício e não
existe integração efetiva com um gateway.

<!-- TODO: Criar o pedido somente depois da confirmação efetiva do pagamento
pelo provider configurado. -->

#### Validações do pedido

- O pedido deve conter entre 1 e 20 itens
- A soma das quantidades não pode ultrapassar 20 pizzas
- Cada quantidade deve estar entre 1 e 20
- O subtotal de cada item deve ser `unit_price × quantity`
- O subtotal do pedido deve corresponder à soma dos itens
- O total deve ser `subtotal + delivery_fee`
- CEP deve conter oito dígitos
- WhatsApp deve conter onze dígitos
- Estado deve conter duas letras maiúsculas
- `idempotency_key` deve ser um UUID válido

#### Idempotência

A mesma combinação de usuário, chave de idempotência e conteúdo retorna o
pedido já persistido. Isso permite repetir uma requisição quando houver dúvida
sobre o recebimento da resposta sem gerar um segundo pedido.

Se a mesma chave for reutilizada pelo usuário com conteúdo diferente, o
serviço retorna `409 Conflict` com o código
`ORDER_SERVICE_IDEMPOTENCY_CONFLICT`.

O identificador do pedido é derivado de `user_id` e `idempotency_key`. A
gravação NoSQL utiliza `IF_ABSENT`, protegendo também requisições concorrentes
com a mesma chave.

### GET `/orders` — Listar meus pedidos

Parâmetros opcionais:

| Parâmetro | Padrão | Regra |
| --- | --- | --- |
| `limit` | `10` | Inteiro entre 1 e 100. |
| `offset` | `0` | Inteiro maior ou igual a zero. |

Exemplo:

```bash
curl --request GET \
  --url 'http://localhost:8004/orders?limit=10&offset=0' \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

Os pedidos são retornados do mais recente para o mais antigo:

```json
{
  "status": "success",
  "data": {
    "orders": []
  }
}
```

Uma lista vazia é uma resposta válida quando o usuário ainda não possui
pedidos.

### GET `/orders/{order_id}` — Consultar meu pedido

```bash
curl --request GET \
  --url http://localhost:8004/orders/ORDER_UUID \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

O pedido somente é retornado quando pertence ao usuário identificado pelo
token. Um UUID inexistente e um pedido pertencente a outro usuário produzem a
mesma resposta `404 Not Found`, evitando revelar a existência de pedidos de
terceiros.

## Operações administrativas

As operações desta seção exigem um JWT válido com as claims de permissão
emitidas pelo `user-service`. Consultas e atualizações aceitam operadores
administrativos ou da cozinha; a exclusão exige um administrador.

### GET `/admin/orders` — Listar todos os pedidos

Parâmetros opcionais:

| Parâmetro | Padrão | Regra |
| --- | --- | --- |
| `order_status` | — | Um dos estados de pedido suportados. |
| `payment_status` | — | Um dos estados de pagamento suportados. |
| `limit` | `10` | Inteiro entre 1 e 100. |
| `offset` | `0` | Inteiro maior ou igual a zero. |

Exemplo:

```bash
curl --request GET \
  --url 'http://localhost:8004/admin/orders?order_status=RECEIVED&payment_status=PAID&limit=20&offset=0' \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

### GET `/admin/orders/summary` — Resumir indicadores dos pedidos

Retorna as quantidades utilizadas pelos painéis administrativo e da cozinha.
O indicador `orders_today` considera o início do dia em UTC. Pedidos pendentes
são aqueles cujo status ainda não é `DELIVERED` nem `CANCELLED`.

```bash
curl --request GET \
  --url http://localhost:8004/admin/orders/summary \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

Exemplo de resposta:

```json
{
  "status": "success",
  "data": {
    "summary": {
      "orders_today": 12,
      "orders_preparing": 4,
      "orders_ready": 2,
      "pending_orders": 8
    }
  }
}
```

### GET `/admin/orders/{order_id}` — Consultar qualquer pedido

```bash
curl --request GET \
  --url http://localhost:8004/admin/orders/ORDER_UUID \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

Ao contrário da rota do usuário, esta consulta não restringe o resultado pelo
proprietário do pedido.

### PATCH `/admin/orders/{order_id}/status` — Atualizar status

```bash
curl --request PATCH \
  --url http://localhost:8004/admin/orders/ORDER_UUID/status \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "status": "PREPARING"
  }'
```

### DELETE `/admin/orders/{order_id}` — Excluir pedido

Remove permanentemente um pedido após a autorização administrativa.

```bash
curl --request DELETE \
  --url http://localhost:8004/admin/orders/ORDER_UUID \
  --header "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

O pedido é removido permanentemente. A atualização de status é realizada pela
rota `PATCH /admin/orders/{order_id}/status`; os estados aceitos são:

| Status | Significado |
| --- | --- |
| `RECEIVED` | Pedido recebido. |
| `PREPARING` | Pedido em preparação. |
| `READY` | Pedido pronto. |
| `OUT_FOR_DELIVERY` | Pedido saiu para entrega. |
| `DELIVERED` | Pedido entregue. |
| `CANCELLED` | Pedido cancelado. |

A implementação atual valida se o valor pertence ao enum, mas não impõe uma
máquina de transição entre os estados.

### Estados de pagamento

Os filtros administrativos reconhecem:

- `PENDING`
- `PAID`
- `FAILED`
- `REFUNDED`
- `CANCELLED`

Não existe atualmente uma rota pública ou administrativa para alterar
`payment_status`.

## Endpoint operacional

### Health check

```bash
curl --request GET \
  --url http://localhost:8004/health \
  --header 'Accept: application/json'
```

Resposta:

```json
{
  "status": "success",
  "data": {
    "service": "order-service"
  }
}
```

## Respostas JSend

Resposta de sucesso:

```json
{
  "status": "success",
  "data": {
    "order": {}
  }
}
```

Resposta de falha:

```json
{
  "status": "fail",
  "data": {
    "code": "ORDER_SERVICE_ORDER_NOT_FOUND",
    "message": "Order not found."
  }
}
```

Erros de validação podem incluir o campo `field`. Exceções inesperadas não
expõem detalhes internos e retornam `Internal server error.`.

## Códigos HTTP

| Status | Uso |
| --- | --- |
| `200 OK` | Consulta ou atualização realizada com sucesso. |
| `201 Created` | Pedido criado ou recuperado idempotentemente pelo `POST /orders`. |
| `400 Bad Request` | Corpo, parâmetro ou UUID rejeitado pela validação. |
| `401 Unauthorized` | Credencial ausente, inválida ou expirada. |
| `403 Forbidden` | Usuário autenticado sem privilégio administrativo. |
| `404 Not Found` | Pedido inexistente ou indisponível ao usuário autenticado. |
| `409 Conflict` | Chave de idempotência reutilizada com conteúdo diferente. |
| `500 Internal Server Error` | Falha interna de criação, consulta, atualização ou erro inesperado. |

Os handlers globais utilizam códigos com o prefixo `ORDER_SERVICE_`:

| Código | Situação |
| --- | --- |
| `ORDER_SERVICE_VALIDATION_ERROR` | Erro de validação da requisição. |
| `ORDER_SERVICE_AUTHENTICATION_ERROR` | Credencial ausente, inválida ou expirada. |
| `ORDER_SERVICE_AUTHORIZATION_ERROR` | Usuário sem privilégio para a operação. |
| `ORDER_SERVICE_HTTP_ERROR` | Outra exceção HTTP conhecida. |
| `ORDER_SERVICE_ORDER_NOT_FOUND` | Pedido não encontrado. |
| `ORDER_SERVICE_IDEMPOTENCY_CONFLICT` | Chave idempotente associada a outro conteúdo. |
| `ORDER_SERVICE_CREATION_ERROR` | Falha interna ao criar um pedido. |
| `ORDER_SERVICE_QUERY_ERROR` | Falha interna ao consultar pedidos. |
| `ORDER_SERVICE_UPDATE_ERROR` | Falha interna ao atualizar um pedido. |
| `ORDER_SERVICE_DELETE_ERROR` | Falha interna ao excluir um pedido. |
| `ORDER_SERVICE_INTERNAL_SERVER_ERROR` | Falha interna inesperada. |

## Configurações

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `APP_NAME` | `order-service` | Nome da aplicação. |
| `APP_ENV` | `development` | Ambiente de execução. |
| `DEBUG` | `false` | Ativa o modo de depuração. |
| `PERSISTENCE_PROVIDER` | `nosql` | Provider de persistência; atualmente a API funciona com `nosql`. |
| `NOSQL_TABLE_NAME` | `orders` | Nome da tabela Oracle NoSQL. |
| `NOSQL_ENDPOINT` | — | Endpoint Oracle NoSQL obrigatório em desenvolvimento. |
| `NOSQL_COMPARTMENT_ID` | — | OCID do compartment relacionado ao NoSQL. |
| `OCI_REGION` | — | Região Oracle NoSQL obrigatória fora de desenvolvimento. |
| `DATABASE_URL` | — | URL reservada para o provider SQLAlchemy. |
| `MESSAGING_PROVIDER` | Obrigatório | Provider de mensageria: `rabbitmq` ou `oci_queue`. |
| `QUEUE_NAME` | `notifications-queue` | Nome lógico da fila de notificações. |
| `RABBITMQ_HOST` | — | Host obrigatório para RabbitMQ. |
| `RABBITMQ_PORT` | — | Porta obrigatória para RabbitMQ. |
| `RABBITMQ_USERNAME` | — | Usuário obrigatório para RabbitMQ. |
| `RABBITMQ_PASSWORD` | — | Senha obrigatória para RabbitMQ. |
| `OCI_QUEUE_ID` | — | OCID obrigatório para OCI Queue. |
| `OCI_QUEUE_MESSAGES_ENDPOINT` | — | Endpoint de mensagens obrigatório para OCI Queue. |
| `HTTP_CLIENT_TIMEOUT` | `10.0` | Timeout da consulta HTTP ao JWKS, em segundos. |
| `JWT_ISSUER` | `user-service` | Emissor esperado no access token. |
| `JWT_AUDIENCE` | `ocipizza` | Audiência esperada no access token. |
| `JWT_JWKS_URL` | `http://user-service:8000/.well-known/jwks.json` | Endpoint das chaves públicas JWT. |
| `LOG_LEVEL` | `INFO` | Nível de logging da aplicação. |
| `OCI_LOG_ID` | — | OCID do Custom Log obrigatório fora de desenvolvimento. |

Os valores refletem os padrões definidos em `app/config/settings.py`. Em
execução local fora do Docker, ajuste `JWT_JWKS_URL` para
`http://localhost:8002/.well-known/jwks.json`. A audiência JWT permanece
`ocipizza` em todos os modos de execução.

## Documentação interativa

Em `development`, o serviço disponibiliza:

- Swagger UI: `http://localhost:8004/docs`
- ReDoc: `http://localhost:8004/redoc`
- OpenAPI JSON: `http://localhost:8004/openapi.json`

Fora de `development`, esses três endpoints são desabilitados. O health check
permanece disponível em `http://localhost:8004/health` para monitoramento da
instância e deve ter sua exposição controlada pela infraestrutura.
