# OCI Pizza — Pizza Service: gerenciamento do catálogo de pizzas

## Responsabilidade do Serviço

O `pizza-service` é responsável pelo catálogo de pizzas da aplicação OCI Pizza.
Suas principais responsabilidades são:

- Cadastrar pizzas
- Consultar e listar pizzas
- Atualizar dados e disponibilidade das pizzas
- Remover pizzas do catálogo
- Classificar pizzas por categoria
- Persistir os dados pertencentes ao seu próprio domínio
- Expor respostas HTTP no padrão JSend

O serviço armazena somente o nome do arquivo de imagem associado à pizza. O
conteúdo da imagem é mantido pelo serviço de Object Storage do ambiente. As
respostas da API incluem `image_name` e a referência da rota privada
`image_url`.

Para preparar o serviço em um ambiente local de desenvolvimento, utilize o
script `bootstrap.sh`.

## Dependências do Serviço

| Componente | Responsabilidade |
| --- | --- |
| Oracle NoSQL | Provider primário e padrão de persistência do catálogo de pizzas. |
| MySQL | Provider alternativo de persistência, acessado por meio do SQLAlchemy. |
| Object Storage | Armazena os arquivos de imagem referenciados pelo campo `image_name`. |
| `user-service` | Publica o JWKS utilizado para validar access tokens JWT nas operações administrativas. |

O serviço utiliza somente um provider de persistência por execução. Oracle
NoSQL é a implementação principal e a configuração padrão; MySQL com
SQLAlchemy é uma segunda opção suportada, selecionada explicitamente pela
configuração do serviço.

O `pizza-service` não acessa diretamente os dados pertencentes a outros
microsserviços.

As rotas de leitura são públicas. As operações de criação, atualização e
exclusão exigem um access token JWT emitido pelo `user-service`, com a claim
`is_admin=true`. O serviço valida o token localmente usando as chaves
publicadas pelo endpoint JWKS; ele não realiza uma chamada ao `user-service`
para cada requisição.

### Dependências Python

As bibliotecas Python são instaladas a partir do arquivo `requirements.txt`:

| Biblioteca | Versão | Uso principal |
| --- | --- | --- |
| FastAPI | 0.141.1 | Implementação da API REST e injeção de dependências. |
| pydantic-settings | 2.10.1 | Leitura e validação das configurações de ambiente. |
| SQLAlchemy | 2.0.43 | Mapeamento ORM do provider relacional alternativo. |
| Alembic | 1.16.5 | Versionamento do schema relacional alternativo. |
| PyMySQL | 1.1.2 | Driver do provider alternativo MySQL. |
| OCI SDK | 2.160.3 | Integração com serviços da Oracle Cloud Infrastructure. |
| MinIO | 7.2.20 | Integração com o Object Storage local em desenvolvimento. |
| borneo | 5.4.3 | SDK de acesso ao Oracle NoSQL Database. |
| PyJWT com extra `crypto` | `>=2.10,<3` | Validação de access tokens JWT assinados. |

O ambiente de execução utiliza Python 3.11.

## `bootstrap.sh` — Bootstrap do ambiente local

O script `bootstrap.sh` cria o ambiente Python, gera a configuração local,
valida os providers configurados, prepara o provider de persistência
selecionado e inclui pizzas de demonstração.

Ele é um script de preparação do ambiente, não o processo principal da API.
Quando `NOSQL_PROVIDER=local`, utiliza o endpoint local configurado. Quando o
provider é diferente de `local`, `NOSQL_COMPARTMENT_ID` é obrigatório para a
configuração do Oracle NoSQL no OCI. A tabela é garantida com a estrutura
necessária sem ser recriada a cada execução.

### Pré-requisitos

- Python 3.11
- Oracle NoSQL local disponível na porta `18080`, quando `NOSQL_PROVIDER=local`
- Credenciais e configuração OCI válidas, quando `NOSQL_PROVIDER=oci`
- MySQL disponível, quando o provider for `sqlalchemy`
- MinIO disponível na porta `9000`, quando `OBJECTSTORAGE_PROVIDER=local`

Para iniciar a infraestrutura padrão a partir da raiz do monorepo, execute:

```bash
make development-infra
```

Ou inicie somente o Oracle NoSQL e o MinIO:

```bash
docker compose up -d nosql object-storage
docker compose ps nosql object-storage
```

### Execução

A partir da raiz do monorepo:

```bash
cd services/pizza-service
./bootstrap.sh
```

Caso o script não possua permissão de execução:

```bash
bash bootstrap.sh
```

A execução foi concluída corretamente quando o terminal exibir:

```text
Bootstrap do pizza-service concluído com sucesso
```

Depois do bootstrap, volte à raiz do monorepo e inicie o serviço:

```bash
cd ../..
docker compose up -d pizza-service
docker compose ps pizza-service
```

### O que o bootstrap executa

1. Valida a disponibilidade do Python 3.11
2. Cria e ativa o ambiente virtual `.venv`
3. Atualiza o `pip` e instala o `requirements.txt`
4. Cria o arquivo `.env`, caso ele ainda não exista
5. Carrega as configurações locais
6. Valida `NOSQL_PROVIDER`, `OBJECTSTORAGE_PROVIDER` e as configurações
   obrigatórias dos providers
7. Identifica o provider definido em `PERSISTENCE_PROVIDER`
8. Cria a tabela `pizzas` no Oracle NoSQL quando o provider é `nosql`
9. Inicializa e executa o Alembic quando o provider é `sqlalchemy`
10. Inclui as pizzas de demonstração que ainda não existem
11. Garante o bucket configurado e envia as imagens de demonstração usando o
    provider selecionado em `OBJECTSTORAGE_PROVIDER`

### Configuração local criada

O `.env` criado pelo bootstrap utiliza:

- `PERSISTENCE_PROVIDER=nosql`
- `NOSQL_PROVIDER=local`
- Tabela `pizzas`
- Oracle NoSQL em `http://localhost:18080`
- `OBJECTSTORAGE_PROVIDER=local`
- MinIO em `http://localhost:9000`
- Bucket `pizza-images`
- Credenciais locais do MinIO `minioadmin`/`minioadmin`
- Emissor JWT `user-service`
- Audiência JWT `ocipizza`
- JWKS em `http://localhost:8002/.well-known/jwks.json`

Se o `.env` já existir, seu conteúdo é preservado. Nesse caso, confira se ele
contém `OBJECTSTORAGE_ENDPOINT`, `OBJECTSTORAGE_BUCKET`,
`OBJECTSTORAGE_ACCESS_KEY` e `OBJECTSTORAGE_SECRET_KEY`.

Para utilizar os recursos OCI no bootstrap, altere `NOSQL_PROVIDER` e/ou
`OBJECTSTORAGE_PROVIDER` para `oci` e configure `OCI_AUTH_MODE`,
`OCI_CONFIG_FILE` (quando aplicável), `OCI_REGION` e
`NOSQL_COMPARTMENT_ID`. Quando o bucket OCI ainda não existir, informe também
`OBJECTSTORAGE_COMPARTMENT_ID`. O bootstrap é interrompido quando um provider
inválido é informado ou quando um compartment obrigatório não está definido.

Exemplo mínimo para autenticação OCI por arquivo de configuração:

```env
NOSQL_PROVIDER=oci
NOSQL_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxxxxx
OBJECTSTORAGE_PROVIDER=oci
OBJECTSTORAGE_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxxxxx
OCI_AUTH_MODE=config_file
OCI_CONFIG_FILE=/home/seu-usuario/.oci/config
OCI_CONFIG_PROFILE=DEFAULT
OCI_REGION=sa-saopaulo-1
```

`OBJECTSTORAGE_COMPARTMENT_ID` só é utilizado quando o bucket precisa ser
criado. Se o bucket já existir, o bootstrap apenas o reutiliza.

## `startdev.sh` — Execução local do serviço

O script `startdev.sh` inicia o `pizza-service` diretamente em modo de
desenvolvimento. Ele carrega o `.env`, aplica os valores padrão para o
Oracle NoSQL, Object Storage e validação JWT, ativa o ambiente virtual
`.venv` preparado pelo bootstrap e inicia o Uvicorn com recarregamento
automático na porta `8001`.

O `startdev.sh` não cria o ambiente virtual, não instala dependências, não
cria a tabela, não cadastra as pizzas de demonstração e não prepara o MinIO.
Execute primeiro o `bootstrap.sh` e garanta que o Oracle NoSQL, o Object
Storage e o `user-service` estejam disponíveis. O script é exclusivo para
desenvolvimento local e não deve ser utilizado como processo de produção.

Para executá-lo:

```bash
cd services/pizza-service
./startdev.sh
```

Caso não possua permissão de execução, utilize:

```bash
bash startdev.sh
```

## Reconstruir a imagem Docker

Após modificar o serviço, reconstrua a imagem a partir da raiz do monorepo:

```bash
docker compose build --no-cache pizza-service
docker compose up -d pizza-service
docker compose ps pizza-service
```

## Persistência

Oracle NoSQL é o provider primário e padrão do `pizza-service`. Como alternativa,
o serviço também pode persistir o catálogo no MySQL por meio do SQLAlchemy. O
provider utilizado em cada execução é selecionado por `PERSISTENCE_PROVIDER`, e
`NOSQL_PROVIDER` seleciona entre o Oracle NoSQL local e o OCI NoSQL.

### Oracle NoSQL

O valor `nosql` utiliza a tabela definida por `NOSQL_TABLE_NAME`. Quando
`NOSQL_PROVIDER=local`, `NOSQL_ENDPOINT` aponta para o container Oracle NoSQL
local. Quando `NOSQL_PROVIDER=oci`, a conexão utiliza a região OCI e a
estratégia definida por `OCI_AUTH_MODE`.

A tabela criada pelo bootstrap possui os campos `id`, `name`, `description`,
`category`, `price`, `image_name`, `available`, `created_at` e `updated_at`.
Durante a criação, o bootstrap aplica limites fixos de capacidade para manter
o ambiente previsível: `read_units=5`, `write_units=5` e `storage_gb=1`.

#### Autenticação OCI

Quando `NOSQL_PROVIDER=oci`, o bootstrap exige `NOSQL_COMPARTMENT_ID` e utiliza
o modo definido em `OCI_AUTH_MODE`:

- `config_file`: exige `OCI_CONFIG_FILE` apontando para o arquivo de
  configuração OCI. `OCI_CONFIG_PROFILE` identifica o profile utilizado; quando
  não informado, o profile padrão do arquivo é utilizado. `OCI_REGION` também
  deve informar a região do Oracle NoSQL.
- `instance_principal`: não utiliza `OCI_CONFIG_FILE` nem
  `OCI_CONFIG_PROFILE`. A execução precisa ocorrer em um recurso OCI com
  Instance Principal configurado e permissões para acessar o NoSQL. A região é
  obtida a partir da identidade do recurso.

O mesmo `OCI_AUTH_MODE` é utilizado pelo Object Storage quando
`OBJECTSTORAGE_PROVIDER=oci`. No modo `config_file`, o arquivo e o profile OCI
devem estar disponíveis no ambiente de execução. No modo `instance_principal`,
o recurso OCI precisa possuir a identidade e as políticas necessárias.

### MySQL com SQLAlchemy — alternativa

O valor `sqlalchemy` utiliza a conexão definida por `DATABASE_URL`. O bootstrap
inicializa o Alembic, gera a migration inicial quando necessário e executa:

```bash
alembic upgrade head
```

## Object Storage e URLs das imagens

O `ObjectStorageService` envia, substitui e remove os arquivos de imagem no
bucket. A leitura das imagens ocorre pelo endpoint da aplicação, sem expor o
bucket privado diretamente ao cliente.

Na criação, o arquivo recebido no campo `image` é enviado ao Object Storage
depois da persistência da pizza. O campo `image` é obrigatório e deve possuir
um `Content-Type` iniciado por `image/`. Quando `image_name` não é informado,
o serviço gera uma chave única no formato `pizza-{uuid}.{extensão}`. Na
atualização, uma nova imagem é enviada somente quando o campo `image` é
informado; se `image_name` não for enviado, uma nova chave é gerada e o objeto
anterior é removido. Na exclusão, o serviço remove a pizza e sua imagem.

Quando `OBJECTSTORAGE_PROVIDER=local`, a URL é formada pela combinação de
`OBJECTSTORAGE_ENDPOINT`, `OBJECTSTORAGE_BUCKET` e o nome do objeto. Quando o
provider é `oci`, a URL regional do OCI Object Storage é utilizada.

Essas URLs pertencem ao armazenamento privado e não devem ser acessadas
diretamente pelo navegador. Para obter uma imagem, utilize a rota
`GET /pizzas/{pizza_id}/image`, que lê o objeto no servidor e devolve seu
conteúdo.

O cliente MinIO utiliza `OBJECTSTORAGE_ACCESS_KEY` e
`OBJECTSTORAGE_SECRET_KEY` para autenticação. O `.env` criado pelo bootstrap e
o `docker-compose.yaml` usam `minioadmin` para ambas as variáveis, de acordo com
as credenciais do MinIO local. Essas credenciais são exclusivas do ambiente de
desenvolvimento. O bucket local permanece privado; o bootstrap apenas garante
sua existência e envia as imagens de demonstração.

No provider OCI, o serviço utiliza `OCI_AUTH_MODE` para autenticação, obtém o
namespace do tenancy e constrói a URL a partir da região, bucket e
`image_name`. O bucket OCI deve estar disponível para a identidade utilizada
na autenticação.

### Validação futura das imagens

Atualmente, o serviço valida se o upload possui conteúdo e um `Content-Type`
de imagem. Essa validação verifica o tipo declarado pelo cliente, mas ainda
não inspeciona o conteúdo binário para confirmar o formato ou a legitimidade
do arquivo. A identificação semântica para confirmar se o arquivo representa
uma pizza ainda não está implementada.

Existe um TODO para integrar o OCI Vision com um modelo customizado e um
limiar de confiança configurável antes da persistência da pizza e do upload no
Object Storage.

## Logging

O logging é configurado durante a inicialização da aplicação:

- Em `development`, os logs são enviados para `stdout`.
- Nos demais ambientes, os logs são enviados ao OCI Logging pela Logging
  Ingestion API, com autenticação via Instance Principal.
- Fora de `development`, `OCI_LOG_ID` é obrigatório e deve conter o OCID do
  Custom Log utilizado para ingestão.

## Pizzas de demonstração

O bootstrap inclui doze pizzas com UUIDs fixos. Entre elas estão Abobrinha,
Bauru, Calabresa, Frango com Bacon, Marguerita, Moda da Casa, Pepperoni e
Portuguesa. O processo consulta o identificador antes da criação e pode ser
executado novamente sem duplicar os registros.

## Como utilizar a API de pizzas

O serviço fica disponível localmente em:

```text
http://localhost:8001
```

Todas as respostas da API seguem o padrão JSend.

### Operações CRUD

| Operação | Método HTTP | Endpoint | Acesso |
| --- | --- | --- | --- |
| READ | `GET` | `/pizzas` | Público. |
| READ | `GET` | `/pizzas/{pizza_id}` | Público. |
| READ | `GET` | `/pizzas/{pizza_id}/image` | Público; retorna a imagem pelo serviço. |
| CREATE | `POST` | `/admin/pizzas` | Administrador. |
| UPDATE | `PUT` | `/admin/pizzas/{pizza_id}` | Administrador. |
| DELETE | `DELETE` | `/admin/pizzas/{pizza_id}` | Administrador. |

As operações administrativas esperam um access token JWT com a claim
`is_admin` igual a `true` no cabeçalho:

```http
Authorization: Bearer <access_token>
```

O token é validado com a chave pública correspondente ao `kid`, obtida no
endpoint JWKS do `user-service`. A validação verifica a assinatura RS256, o
emissor, a audiência e a expiração do token. Após a validação, a claim `sub`
deve conter um UUID válido e a claim `is_admin` deve ser `true`.

### READ — Listar pizzas

```bash
curl --request GET \
  --url 'http://localhost:8001/pizzas?category=salgada&available=true&limit=10&offset=0' \
  --header 'Accept: application/json'
```

Todos os parâmetros são opcionais:

| Parâmetro | Descrição |
| --- | --- |
| `category` | Categoria da pizza: `salgada`, `vegetariana` ou `doce`. |
| `available` | Filtra pela disponibilidade; aceita `true` ou `false`. |
| `limit` | Quantidade máxima retornada, entre 1 e 100; o padrão é 10. |
| `offset` | Quantidade de registros ignorados; o padrão é 0. |

O sucesso retorna `200 OK` e uma lista em `data.pizzas`. Quando nenhum registro
corresponde aos filtros, a lista é vazia. Falhas de consulta resultam em
`500 Internal Server Error`. Cada item inclui `image_name` e `image_url`.

### READ — Consultar uma pizza

Substitua `PIZZA_ID` pelo UUID da pizza:

```bash
curl --request GET \
  --url http://localhost:8001/pizzas/PIZZA_ID \
  --header 'Accept: application/json'
```

O sucesso retorna `200 OK` e a pizza em `data.pizza`. Um identificador válido
sem registro correspondente resulta em `404 Not Found`. Um valor que não seja
UUID resulta em `400 Bad Request`. A resposta da pizza inclui a URL completa da
imagem no campo `image_url`.

### READ — Obter a imagem de uma pizza

```bash
curl --request GET \
  --url http://localhost:8001/pizzas/PIZZA_ID/image
```

O endpoint consulta o objeto no bucket privado e devolve o conteúdo da imagem
com o `Content-Type` armazenado. A aplicação não exige que o bucket seja
público para disponibilizar essa rota. Pizza inexistente resulta em `404 Not
Found`; falhas de leitura do Object Storage resultam em `500 Internal Server
Error`.

### CREATE — Criar uma pizza

```bash
curl --request POST \
  --url http://localhost:8001/admin/pizzas \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --form 'name=Margherita Especial' \
  --form 'description=Molho de tomate, mussarela e manjericão.' \
  --form 'category=vegetariana' \
  --form 'price=49.90' \
  --form 'available=true' \
  --form 'image=@/caminho/pizza-margherita-especial.jpg;type=image/jpeg'
```

A requisição utiliza `multipart/form-data`. Os dados da pizza são enviados como
campos de formulário e o campo `image` contém o arquivo que será armazenado no
Object Storage.

| Campo | Regra |
| --- | --- |
| `name` | Obrigatório; entre 1 e 100 caracteres. |
| `description` | Obrigatório; entre 1 e 500 caracteres. |
| `category` | Obrigatório; `salgada`, `vegetariana` ou `doce`. |
| `price` | Obrigatório; deve ser maior que zero. |
| `image_name` | Opcional; entre 1 e 255 caracteres. Se omitido, é gerado pelo serviço. |
| `image` | Obrigatório; arquivo não vazio com um `Content-Type` de imagem. |
| `available` | Opcional; o padrão é `true`. |

O sucesso retorna `201 Created` e a pizza criada em `data.pizza`, incluindo a
referência da rota privada da imagem em `image_url`. Erros de validação retornam `400 Bad Request`; falhas de
persistência, upload da imagem ou construção da URL retornam `500 Internal
Server Error`.

### UPDATE — Atualizar uma pizza

O update é parcial: somente os campos enviados são alterados, apesar de a rota
utilizar o método HTTP `PUT`.

```bash
curl --request PUT \
  --url http://localhost:8001/admin/pizzas/PIZZA_ID \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --form 'price=54.90' \
  --form 'available=true' \
  --form 'image=@/caminho/pizza-margherita-atualizada.jpg;type=image/jpeg'
```

A requisição utiliza `multipart/form-data`. Todos os campos da pizza são
opcionais. O arquivo `image` também é opcional; quando enviado, deve ser não
vazio e possuir um `Content-Type` de imagem. Se `image_name` for informado
junto com o arquivo, a nova imagem é armazenada com esse nome. Caso contrário,
o serviço gera uma nova chave e remove a imagem anterior do Object Storage.

Quando informado, `price` deve ser maior que zero e possuir no máximo duas
casas decimais. O sucesso retorna `200 OK`; pizza inexistente resulta em `404
Not Found`; falhas de persistência ou de atualização da imagem resultam em `500
Internal Server Error`. A resposta atualizada inclui a referência da rota
privada em `image_url`.

### DELETE — Excluir uma pizza

```bash
curl --request DELETE \
  --url http://localhost:8001/admin/pizzas/PIZZA_ID \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

O sucesso retorna `200 OK` e a mensagem `Pizza deleted successfully.`. Pizza
inexistente resulta em `404 Not Found`; falhas de persistência ou de remoção da
imagem resultam em `500 Internal Server Error`.

A remoção do registro e a remoção do objeto são operações separadas; se a
exclusão do objeto falhar, a API retorna erro mesmo que o registro já tenha
sido removido. O tratamento de consistência entre essas operações está
registrado como TODO no serviço.

## Modelo retornado pela API

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id` | UUID | Identificador da pizza. |
| `name` | string | Nome da pizza. |
| `description` | string | Descrição e ingredientes. |
| `category` | string | `salgada`, `vegetariana` ou `doce`. |
| `price` | decimal | Preço da pizza. |
| `image_name` | string | Nome do arquivo armazenado no Object Storage. |
| `image_url` | string | URL da rota privada usada para obter a imagem. |
| `available` | boolean | Indica se a pizza pode ser comercializada. |
| `created_at` | datetime | Data e hora de criação. |
| `updated_at` | datetime | Data e hora da última atualização. |

## Endpoint operacional

### Health check

```bash
curl --request GET \
  --url http://localhost:8001/health \
  --header 'Accept: application/json'
```

O endpoint retorna `200 OK` no padrão JSend quando a aplicação está ativa.

## Respostas JSend

Resposta de sucesso:

```json
{
  "status": "success",
  "data": {
    "pizza": {
      "id": "33333333-3333-4333-8333-333333333333",
      "name": "Calabresa",
      "description": "Molho de tomate, mussarela, calabresa e cebola.",
      "category": "salgada",
      "price": "49.90",
      "image_name": "pizza-calabresa.jpg",
      "image_url": "/pizzas/33333333-3333-4333-8333-333333333333/image",
      "available": true,
      "created_at": "2026-10-03T12:00:00Z",
      "updated_at": "2026-10-03T12:00:00Z"
    }
  }
}
```

Resposta de falha:

```json
{
  "status": "fail",
  "data": {
    "code": "PIZZA_SERVICE_PIZZA_NOT_FOUND",
    "message": "Pizza not found."
  }
}
```

Erros de validação incluem também o campo `field`. Exceções inesperadas não
expõem detalhes internos e retornam `INTERNAL_SERVER_ERROR`.

## Códigos HTTP

| Status | Uso |
| --- | --- |
| `200 OK` | Consultas, atualizações e exclusões concluídas. |
| `201 Created` | Pizza criada. |
| `400 Bad Request` | Payload, parâmetro ou UUID inválido. |
| `401 Unauthorized` | Access token ausente ou inválido. |
| `403 Forbidden` | Usuário autenticado sem privilégio administrativo. |
| `404 Not Found` | Pizza não encontrada. |
| `500 Internal Server Error` | Falha interna de consulta, persistência, armazenamento ou comunicação com o JWKS. |

## Configurações

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `APP_NAME` | `pizza-service` | Nome da aplicação. |
| `APP_ENV` | `development` | Ambiente de execução. |
| `DEBUG` | `false` | Ativa o modo de depuração. |
| `PERSISTENCE_PROVIDER` | `nosql` | Provider de persistência: `nosql` (primário e padrão) ou `sqlalchemy` (alternativo). |
| `NOSQL_PROVIDER` | `local` | Backend NoSQL: `local` ou `oci`. |
| `NOSQL_TABLE_NAME` | `pizzas` | Nome da tabela Oracle NoSQL. |
| `NOSQL_ENDPOINT` | — | Endpoint utilizado quando `NOSQL_PROVIDER=local`. |
| `NOSQL_COMPARTMENT_ID` | — | OCID do compartment relacionado ao NoSQL. |
| `DATABASE_URL` | — | URL de conexão utilizada pelo SQLAlchemy. |
| `DATABASE_PROVIDER` | `local` | Provider de banco relacional reservado para o SQLAlchemy. |
| `OCI_REGION` | `sa-saopaulo-1` | Região utilizada pelos providers OCI. |
| `OCI_AUTH_MODE` | `config_file` | Autenticação OCI: `config_file` ou `instance_principal`. |
| `OCI_CONFIG_FILE` | — | Caminho do arquivo de configuração OCI quando aplicável. |
| `OCI_CONFIG_PROFILE` | `DEFAULT` | Profile do arquivo de configuração OCI. |
| `JWT_ISSUER` | `user-service` | Emissor esperado no JWT. |
| `JWT_AUDIENCE` | `ocipizza` | Audiência esperada no JWT. |
| `JWT_JWKS_URL` | `http://user-service:8000/.well-known/jwks.json` | URL das chaves públicas JWT. |
| `OBJECTSTORAGE_PROVIDER` | `local` | Backend de objetos: `local` ou `oci`. |
| `OBJECTSTORAGE_ENDPOINT` | `http://object-storage:9000` | Endpoint utilizado pelo provider local. |
| `OBJECTSTORAGE_BUCKET` | `pizza-images` | Nome do bucket de imagens. |
| `OBJECTSTORAGE_COMPARTMENT_ID` | — | Compartment usado para criar o bucket OCI quando ele ainda não existe. |
| `OBJECTSTORAGE_ACCESS_KEY` | — | Chave do MinIO, obrigatória no provider local. |
| `OBJECTSTORAGE_SECRET_KEY` | — | Chave secreta do MinIO, obrigatória no provider local. |
| `LOG_LEVEL` | `INFO` | Nível de logging da aplicação. |
| `OCI_LOG_ID` | — | OCID do Custom Log fora de desenvolvimento. |

## Documentação interativa

Em `development`, o serviço disponibiliza:

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- OpenAPI JSON: `http://localhost:8001/openapi.json`

Fora de `development`, esses três endpoints são desabilitados. O health check
permanece disponível em `http://localhost:8001/health` para monitoramento da
instância e deve ter sua exposição controlada pela infraestrutura.
