# OCI Pizza — Delivery Service: cotação e administração de entrega

## Responsabilidade do Serviço

O `delivery-service` é responsável por consultar a elegibilidade e a cotação
de entrega dos pedidos da OCI Pizza e por administrar as áreas atendidas pela
pizzaria. O serviço responde a duas perguntas:

1. A pizzaria entrega no CEP informado?
2. Quando a entrega está disponível, qual é a taxa e o prazo estimado?

Suas principais responsabilidades são:

- Normalizar e validar o CEP recebido
- Localizar uma faixa de CEP ativa
- Informar se a entrega está disponível
- Retornar a taxa e o prazo estimado da entrega
- Persistir as áreas de entrega pertencentes ao seu domínio
- Validar access tokens JWT antes de realizar uma cotação
- Restringir as operações administrativas a usuários com `is_admin=true`
- Expor respostas HTTP no padrão JSend

O serviço não acessa dados de pedidos, usuários ou pizzas. Para preparar o
ambiente local de desenvolvimento, utilize o script `bootstrap.sh`.

## Dependências do Serviço

| Componente | Responsabilidade |
| --- | --- |
| Oracle NoSQL | Provider primário e atualmente implementado para persistência das áreas de entrega. |
| `user-service` | Publica o JWKS e emite os access tokens JWT utilizados na autenticação. |

O Oracle NoSQL é o provider padrão do serviço. Embora existam dependências e
estruturas iniciais para SQLAlchemy no projeto, o repositório relacional de
áreas de entrega ainda não implementa as operações de persistência e o
bootstrap aceita somente `PERSISTENCE_PROVIDER=nosql`.

### Dependências Python

As bibliotecas são instaladas a partir do arquivo `requirements.txt`:

| Biblioteca | Versão | Uso principal |
| --- | --- | --- |
| FastAPI | 0.141.1 | Implementação da API REST e injeção de dependências. |
| pydantic-settings | 2.10.1 | Leitura e validação das configurações de ambiente. |
| HTTPX | 0.28.1 | Consulta assíncrona ao JWKS publicado pelo `user-service`. |
| SQLAlchemy | 2.0.43 | Estrutura do provider relacional alternativo. |
| Alembic | 1.16.5 | Versionamento previsto para o schema relacional. |
| PyMySQL | 1.1.2 | Driver previsto para a conexão MySQL. |
| PyJWT com extra `crypto` | `>=2.10,<3` | Validação de access tokens JWT assinados com RS256. |
| OCI SDK | 2.160.3 | Envio de logs ao OCI Logging. |
| borneo | 5.4.3 | Acesso ao Oracle NoSQL Database. |

O ambiente de execução utiliza Python 3.11.

## `bootstrap.sh` — Bootstrap do ambiente local

O script `bootstrap.sh` prepara o ambiente Python, cria a configuração local,
identifica o provider NoSQL selecionado, garante a tabela e cadastra as áreas
de entrega utilizadas em desenvolvimento.

Ele é um script de preparação do ambiente, não o processo principal da API:
deve ser executado antes da primeira inicialização ou quando for necessário
recarregar a tabela e as áreas de demonstração.

> **Atenção:** a tabela não é excluída durante o bootstrap. Os dados de
> demonstração são inseridos de forma idempotente, portanto execuções
> repetidas não duplicam áreas já cadastradas.

### Pré-requisitos

- Python 3.11
- Oracle NoSQL local disponível na porta `18080`, quando
  `NOSQL_PROVIDER=local`; ou acesso configurado ao OCI NoSQL, quando
  `NOSQL_PROVIDER=oci`

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
cd services/delivery-service
./bootstrap.sh
```

Caso o script não possua permissão de execução:

```bash
bash bootstrap.sh
```

A execução foi concluída corretamente quando o terminal exibir:

```text
Bootstrap do delivery-service concluído com sucesso
```

Depois do bootstrap, volte à raiz do monorepo e inicie o serviço:

```bash
cd ../..
docker compose up -d delivery-service
docker compose ps delivery-service
```

### O que o bootstrap executa

1. Valida a disponibilidade do Python 3.11
2. Cria e ativa o ambiente virtual `.venv`
3. Atualiza o `pip` e instala o `requirements.txt`
4. Cria o arquivo `.env`, caso ele ainda não exista
5. Carrega as configurações locais
6. Carrega e valida `NOSQL_PROVIDER` e as configurações obrigatórias do OCI
7. Garante a tabela configurada em `NOSQL_TABLE_NAME`
8. Cria a tabela com `read_units=5`, `write_units=5` e `storage_gb=1`
9. Em `APP_ENV=development`, cadastra as 30 faixas de CEP de demonstração
10. Confirma que os 30 registros foram efetivamente persistidos

Os UUIDs das áreas são derivados de suas faixas de CEP. Dessa forma, o
bootstrap pode ser executado novamente com os mesmos identificadores sem
duplicar registros. O seed só é executado em `APP_ENV=development`, e o
script termina com erro se a quantidade persistida for diferente de 30.

### Configuração local criada

O `.env` criado pelo bootstrap utiliza:

- `APP_NAME=delivery-service`
- `APP_ENV=development`
- `PERSISTENCE_PROVIDER=nosql`
- `NOSQL_PROVIDER=local`
- Tabela `delivery_areas`
- Oracle NoSQL em `http://localhost:18080`
- `NOSQL_COMPARTMENT_ID` vazio para o provider local
- `OCI_AUTH_MODE=config_file`, com profile `DEFAULT`
- Emissor JWT `user-service`
- Audiência JWT `ocipizza`
- JWKS em `http://localhost:8002/.well-known/jwks.json`
- Logging com nível `INFO`

Se o `.env` já existir, seu conteúdo será preservado.

## `startdev.sh` — Execução local do serviço

O script `startdev.sh` inicia o `delivery-service` diretamente no ambiente de
desenvolvimento. Ele carrega o `.env`, aplica valores padrão, valida o
provider NoSQL e as configurações de autenticação OCI, ativa o ambiente
virtual preparado pelo `bootstrap.sh` e inicia o Uvicorn com recarregamento
automático na porta `8003`.

O `startdev.sh` não cria o ambiente virtual, instala dependências, recria a
tabela nem cadastra as áreas de demonstração. Execute primeiro o
`bootstrap.sh` e garanta que o backend NoSQL e o `user-service` estejam
disponíveis. O script é exclusivo para desenvolvimento local e não deve ser
utilizado como processo de produção.

Para executá-lo:

```bash
cd services/delivery-service
./startdev.sh
```

Caso não possua permissão de execução, utilize:

```bash
bash startdev.sh
```

## Reconstruir a imagem Docker

Após modificar o serviço, reconstrua sua imagem a partir da raiz do monorepo:

```bash
docker compose build --no-cache delivery-service
docker compose up -d delivery-service
docker compose ps delivery-service
```

## Persistência

### Oracle NoSQL

O valor `nosql` utiliza a tabela definida por `NOSQL_TABLE_NAME`. Quando
`NOSQL_PROVIDER=local`, `NOSQL_ENDPOINT` aponta para o Oracle NoSQL local.
Quando `NOSQL_PROVIDER=oci`, o serviço utiliza o Oracle NoSQL Cloud Service,
exige `NOSQL_COMPARTMENT_ID` e autentica conforme `OCI_AUTH_MODE`:

- `config_file`: exige `OCI_CONFIG_FILE` e utiliza `OCI_CONFIG_PROFILE`.
- `instance_principal`: utiliza a identidade da instância no OCI.

`OCI_REGION` identifica a região quando o modo `config_file` é utilizado.

A tabela `delivery_areas` contém os campos:

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id` | string/UUID | Identificador único da área. |
| `name` | string | Nome interno da área de entrega. |
| `zip_code_start` | string | Primeiro CEP da faixa. |
| `zip_code_end` | string | Último CEP da faixa. |
| `delivery_fee` | number | Taxa de entrega. |
| `estimated_minutes` | integer | Prazo estimado em minutos. |
| `active` | boolean | Indica se a faixa está disponível para cotação. |
| `created_at` | timestamp | Data e hora de criação. |
| `updated_at` | timestamp | Data e hora da última atualização. |

A consulta considera somente áreas ativas cujo CEP esteja entre
`zip_code_start` e `zip_code_end`.

## Logging

O logging é configurado durante a inicialização da aplicação:

- Os logs são sempre enviados para `stdout`.
- Fora de `development`, eles também são enviados ao OCI Logging pela Logging
  Ingestion API.
- A autenticação no OCI Logging utiliza Instance Principal.
- Fora de `development`, `OCI_LOG_ID` é obrigatório.
- Exceções inesperadas são registradas antes da resposta HTTP 500.

## Como utilizar a API de entrega

O serviço fica disponível localmente em:

```text
http://localhost:8003
```

As respostas da API seguem o padrão JSend.

### Rotas disponíveis

| Operação | Método HTTP | Endpoint | Acesso |
| --- | --- | --- | --- |
| Cotar entrega | `GET` | `/delivery/quote/{zip_code}` | Usuário autenticado. |
| Listar áreas | `GET` | `/admin/delivery/areas` | Administrador. |
| Consultar área | `GET` | `/admin/delivery/areas/{delivery_area_id}` | Administrador. |
| Criar área | `POST` | `/admin/delivery/areas` | Administrador. |
| Atualizar área | `PUT` | `/admin/delivery/areas/{delivery_area_id}` | Administrador. |
| Excluir área | `DELETE` | `/admin/delivery/areas/{delivery_area_id}` | Administrador. |
| Alterar status | `PATCH` | `/admin/delivery/areas/{delivery_area_id}/active` | Administrador. |
| Health check | `GET` | `/health` | Público. |

As rotas administrativas retornam respostas JSend. A listagem aceita os
parâmetros opcionais `active`, `limit` e `offset`.

## Autenticação

A cotação exige um access token JWT no cabeçalho `Authorization`:

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

As rotas administrativas exigem adicionalmente a claim `is_admin=true`. A
claim `role` não é utilizada pelo contrato de autenticação do serviço.

As chaves públicas são mantidas em memória. O serviço tenta aquecer esse cache
durante a inicialização, mas uma indisponibilidade momentânea do `user-service`
não impede que o `delivery-service` seja iniciado. Caso a chave solicitada não
esteja no cache, o JWKS é consultado novamente.

## Cotação e elegibilidade por CEP

### GET `/delivery/quote/{zip_code}`

Exemplo utilizando um CEP sem formatação:

```bash
curl --request GET \
  --url http://localhost:8003/delivery/quote/18000001 \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

O CEP também pode ser informado com hífen:

```bash
curl --request GET \
  --url http://localhost:8003/delivery/quote/18000-001 \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

Antes da consulta, todos os caracteres não numéricos são removidos. O valor
normalizado deve conter exatamente oito dígitos.

O mesmo formato canônico é utilizado nas faixas persistidas e nas respostas
da API. O hífen pertence somente à apresentação em interfaces de usuário.

### Entrega disponível

Quando existe uma faixa ativa que contempla o CEP, o serviço retorna `200 OK`:

```json
{
  "status": "success",
  "data": {
    "available": true,
    "delivery_fee": "5.0",
    "estimated_minutes": 30
  }
}
```

`delivery_fee` é retornado como string para preservar a representação decimal.

### Entrega indisponível

Quando não existe uma faixa ativa para o CEP, o resultado também é `200 OK`:

```json
{
  "status": "success",
  "data": {
    "available": false,
    "delivery_fee": null,
    "estimated_minutes": null
  }
}
```

Uma faixa cadastrada com `active=false` é tratada como indisponível para fins
de cotação.

## Administração das áreas de entrega

As operações administrativas permitem cadastrar e manter as faixas atendidas
pela pizzaria. Na criação, o serviço normaliza os CEPs, valida que o CEP
inicial não seja maior que o final e persiste a taxa, o prazo e o status da
área.

Na atualização, os campos são parciais: valores não enviados permanecem
inalterados. A alteração do status também pode ser feita isoladamente pelo
endpoint `PATCH /admin/delivery/areas/{delivery_area_id}/active`.

Exemplo de criação:

```bash
curl --request POST \
  --url http://localhost:8003/admin/delivery/areas \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "Centro",
    "zip_code_start": "18000000",
    "zip_code_end": "18100999",
    "delivery_fee": "10.00",
    "estimated_minutes": 40,
    "active": true
  }'
```

## Endpoint operacional

### Health check

```bash
curl --request GET \
  --url http://localhost:8003/health \
  --header 'Accept: application/json'
```

O endpoint retorna `200 OK` no padrão JSend quando a aplicação está ativa.

## Respostas JSend

Resposta de sucesso:

```json
{
  "status": "success",
  "data": {
    "available": true,
    "delivery_fee": "5.0",
    "estimated_minutes": 30
  }
}
```

Resposta de falha:

```json
{
  "status": "fail",
  "data": {
    "code": "DELIVERY_SERVICE_AUTHENTICATION_ERROR",
    "message": "Not authenticated"
  }
}
```

Erros de validação podem incluir o campo `field`. Exceções inesperadas não
expõem detalhes internos e retornam a mensagem `Internal server error.`.

## Códigos HTTP

| Status | Uso |
| --- | --- |
| `200 OK` | Cotação realizada, independentemente da disponibilidade da entrega. |
| `400 Bad Request` | Parâmetro ou requisição rejeitada pela validação do FastAPI. |
| `401 Unauthorized` | Cabeçalho Bearer ausente ou malformado, token expirado ou token JWT inválido. |
| `500 Internal Server Error` | Falha inesperada, CEP inválido ou indisponibilidade não tratada de uma dependência. |

Os handlers globais utilizam códigos com o prefixo `DELIVERY_SERVICE_`:

| Código | Situação |
| --- | --- |
| `DELIVERY_SERVICE_VALIDATION_ERROR` | Erro de validação da requisição. |
| `DELIVERY_SERVICE_AUTHENTICATION_ERROR` | Credencial ausente, inválida ou expirada. |
| `DELIVERY_SERVICE_AUTHORIZATION_ERROR` | Usuário autenticado sem permissão para a operação. |
| `DELIVERY_SERVICE_HTTP_ERROR` | Outra exceção HTTP conhecida. |
| `DELIVERY_SERVICE_INTERNAL_SERVER_ERROR` | Falha interna inesperada. |

## Configurações

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `APP_NAME` | `delivery-service` | Nome da aplicação. |
| `APP_ENV` | `development` | Ambiente de execução. |
| `DEBUG` | `false` | Ativa o modo de depuração. |
| `PERSISTENCE_PROVIDER` | `nosql` | Provider de persistência; atualmente o serviço funciona com `nosql`. |
| `NOSQL_PROVIDER` | `local` | Backend NoSQL: `local` ou `oci`. |
| `NOSQL_TABLE_NAME` | `delivery_areas` | Nome da tabela Oracle NoSQL. |
| `NOSQL_ENDPOINT` | `http://localhost:18080` | Endpoint do Oracle NoSQL local quando `NOSQL_PROVIDER=local`. |
| `NOSQL_COMPARTMENT_ID` | — | OCID obrigatório quando `NOSQL_PROVIDER=oci`. |
| `OCI_REGION` | `sa-saopaulo-1` | Região usada no acesso ao OCI NoSQL com arquivo de configuração. |
| `OCI_AUTH_MODE` | `config_file` | Autenticação OCI: `config_file` ou `instance_principal`. |
| `OCI_CONFIG_FILE` | — | Caminho do arquivo OCI quando `OCI_AUTH_MODE=config_file`. |
| `OCI_CONFIG_PROFILE` | `DEFAULT` | Profile do arquivo de configuração OCI. |
| `DATABASE_URL` | — | URL reservada para o provider SQLAlchemy. |
| `HTTP_CLIENT_TIMEOUT` | `10.0` | Timeout da consulta HTTP ao JWKS, em segundos. |
| `JWT_ISSUER` | `user-service` | Emissor esperado no access token. |
| `JWT_AUDIENCE` | `ocipizza` | Audiência esperada no access token. |
| `JWT_JWKS_URL` | `http://user-service:8000/.well-known/jwks.json` | Endpoint das chaves públicas JWT. |
| `LOG_LEVEL` | `INFO` | Nível de logging da aplicação. |
| `OCI_LOG_ID` | — | OCID do Custom Log obrigatório fora de desenvolvimento. |

Os valores da tabela refletem os padrões definidos atualmente em
`app/config/settings.py`, `bootstrap.sh` e `startdev.sh`. O bootstrap
preserva um `.env` já existente.

## Documentação interativa

Em `development`, o serviço disponibiliza:

- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`
- OpenAPI JSON: `http://localhost:8003/openapi.json`

Fora de `development`, esses três endpoints são desabilitados. O health check
permanece disponível em `http://localhost:8003/health` para monitoramento da
instância e deve ter sua exposição controlada pela infraestrutura.
