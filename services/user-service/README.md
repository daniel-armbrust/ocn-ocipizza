# OCI Pizza — User Service: gerenciamento de usuários e credenciais

## Responsabilidade do Serviço

O `user-service` é responsável pelo ciclo de vida dos usuários da aplicação
OCI Pizza. Suas principais responsabilidades são:

- Cadastrar usuários
- Consultar e atualizar dados de perfil
- Gerenciar credenciais dos usuários
- Permitir a troca de senha do usuário autenticado
- Gerenciar o fluxo de solicitação e confirmação de redefinição de senha
- Persistir os dados pertencentes ao seu próprio domínio
- Publicar solicitações de envio de e-mail por meio de mensageria
- Preservar o isolamento de dados, sem acessar bancos de outros microsserviços

Para preparar o serviço em um ambiente local de desenvolvimento, utilize o
script `bootstrap.sh`.

## Dependências do Serviço

O `user-service` depende dos seguintes componentes para funcionar no ambiente
de desenvolvimento:

| Componente | Responsabilidade |
| --- | --- |
| MySQL | Provider de persistência para armazenar usuários, tokens e históricos de senha. |
| OCI NoSQL | Provider de persistência para armazenar usuários, tokens e históricos de senha. |
| RabbitMQ | Publica mensagens assíncronas, como solicitações de envio de e-mail. |

O serviço não acessa diretamente o banco de dados de outro microsserviço. No
Docker Compose, MySQL, RabbitMQ e OCI NoSQL são serviços de infraestrutura
independentes. O `user-service` pode utilizar MySQL ou OCI NoSQL como provider
de persistência e RabbitMQ como provider de mensageria.

### Dependências Python

As bibliotecas Python são instaladas a partir do arquivo `requirements.txt`:

| Biblioteca | Versão | Uso principal |
| --- | --- | --- |
| FastAPI | 0.141.1 | Implementação da API REST e injeção de dependências. |
| pydantic-settings | 2.10.1 | Leitura e validação das configurações de ambiente. |
| SQLAlchemy | 2.0.43 | Mapeamento ORM e acesso ao banco de dados. |
| Alembic | 1.16.5 | Criação e aplicação das migrations do banco de dados. |
| PyMySQL | 1.1.2 | Driver de conexão entre SQLAlchemy e MySQL. |
| pika | 1.3.2 | Comunicação com o RabbitMQ. |
| OCI SDK | 2.160.3 | Integração com provedores da Oracle Cloud Infrastructure. |
| PyJWT com extra `crypto` | `>=2.10,<3` | Suporte à criação, assinatura e validação de tokens JWT. |
| passlib | 1.7.4 | Suporte a mecanismos de proteção de senhas. |
| bcrypt | 4.3.0 | Suporte ao algoritmo de hash bcrypt. |

O ambiente de execução do serviço utiliza Python 3.11. Não instale essas
bibliotecas manualmente uma a uma: o bootstrap realiza a instalação das versões
definidas em `requirements.txt`.

## Configurações

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `APP_NAME` | `user-service` | Nome da aplicação. |
| `APP_ENV` | `development` | Ambiente de execução. |
| `DEBUG` | `false` | Ativa o modo de depuração. |
| `PERSISTENCE_PROVIDER` | `sqlalchemy` | Provider de persistência: `sqlalchemy` ou `nosql`. |
| `DATABASE_URL` | — | URL de conexão utilizada pelo SQLAlchemy. |
| `MESSAGING_PROVIDER` | — | Provider de mensageria: `rabbitmq` ou `oci_queue`. |
| `RABBITMQ_HOST` | — | Host do RabbitMQ. |
| `RABBITMQ_PORT` | — | Porta do RabbitMQ. |
| `RABBITMQ_USERNAME` | — | Usuário utilizado na conexão com o RabbitMQ. |
| `RABBITMQ_PASSWORD` | — | Senha utilizada na conexão com o RabbitMQ. |
| `RABBITMQ_QUEUE_NAME` | — | Nome da fila de notificações no RabbitMQ. |
| `OCI_QUEUE_ID` | — | OCID da fila utilizada pelo provider OCI Queue. |
| `OCI_QUEUE_MESSAGES_ENDPOINT` | — | Endpoint de mensagens da OCI Queue. |
| `OCI_REGION` | — | Região dos serviços OCI utilizados pela instância. |
| `JWT_KEY_PROVIDER` | `local` | Provider das chaves JWT: `local` ou `oci`. |
| `JWT_ISSUER` | `user-service` | Emissor incluído e esperado nos access tokens. |
| `JWT_AUDIENCE` | `oci-pizza` | Audiência incluída e esperada nos access tokens. |
| `JWT_ACCESS_TOKEN_EXPIRATION_MINUTES` | `15` | Validade do access token em minutos. |
| `JWT_PRIVATE_KEY_PATH` | `/run/secrets/jwt_private_key.pem` | Caminho da chave privada RSA local. |
| `JWT_PUBLIC_KEY_PATH` | `/run/secrets/jwt_public_key.pem` | Caminho da chave pública RSA local. |
| `JWT_PRIVATE_KEY_SECRET_ID` | — | OCID do secret que contém a chave privada no provider OCI. |
| `REFRESH_TOKEN_EXPIRATION_DAYS` | `30` | Validade do refresh token em dias. |
| `LOG_LEVEL` | `INFO` | Nível global de logging da aplicação. |
| `OCI_LOG_ID` | — | OCID do Custom Log, obrigatório fora de desenvolvimento. |

## Documentação interativa

Em `development`, o serviço disponibiliza:

- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`
- OpenAPI JSON: `http://localhost:8002/openapi.json`

Fora de `development`, esses três endpoints são desabilitados. O health check
permanece disponível em `http://localhost:8002/health` para monitoramento da
instância e deve ter sua exposição controlada pela infraestrutura.

## `bootstrap.sh` — Bootstrap do ambiente local

O script `bootstrap.sh` automatiza a criação do ambiente Python, a configuração do banco de
dados, a execução das migrations e a inclusão dos usuários de demonstração.

> O bootstrap foi desenvolvido exclusivamente para desenvolvimento local. As
> credenciais padrão usadas pelo script não devem ser reutilizadas em ambientes
> de produção.

### Pré-requisitos

Antes de executar o `bootstrap.sh`, inicie somente o MySQL e o RabbitMQ. O
`user-service` deve ser iniciado depois do bootstrap, pois o script gera as
chaves JWT, prepara o banco de dados e aplica as migrations utilizadas pelo
container.

### Passo a passo

#### 1. Acesse a raiz do monorepo

Abra um terminal e acesse o diretório em que o OCI Pizza foi clonado:

```bash
cd /caminho/para/ocn-ocipizza
```

Nos próximos passos, a expressão “raiz do monorepo” se refere a esse diretório,
que contém o arquivo `docker-compose.yaml` e o diretório `services`.

#### 2. Inicie os serviços necessários

Ainda na raiz do monorepo, escolha apenas uma das alternativas a seguir.

Para iniciar toda a infraestrutura de desenvolvimento, execute:

```bash
make development-infra
```

Esse é o comando padrão do projeto. Ele inicia MySQL, Oracle NoSQL e RabbitMQ e
aguarda até que a infraestrutura esteja disponível.

Para iniciar somente os componentes necessários ao desenvolvimento do
`user-service`, execute:

```bash
docker compose up -d mysql nosql rabbitmq
```

O argumento `-d` executa o container em segundo plano e libera o terminal para
os próximos comandos.

#### 3. Verifique o estado dos serviços

Execute:

```bash
docker compose ps mysql nosql rabbitmq
```

Na coluna de estado, confirme que o MySQL, o OCI NoSQL e o RabbitMQ estão em
execução e aguarde até que o MySQL e o RabbitMQ apareçam como `healthy`. O OCI
NoSQL não possui health check configurado no Docker Compose. O bootstrap também
espera o MySQL aceitar conexões, mas essa verificação ajuda a identificar
antecipadamente problemas na inicialização dos containers.

#### 4. Acesse o diretório do user-service

A partir da raiz do monorepo, execute:

```bash
cd services/user-service
```

Confirme que está no diretório correto:

```bash
pwd
ls requirements.txt bootstrap.sh
```

O comando `ls` deve exibir os dois arquivos. O bootstrap será interrompido se
for executado fora desse diretório.

#### 5. Execute o bootstrap

Execute:

```bash
./bootstrap.sh
```

Caso o terminal mostre a mensagem `Permission denied`, execute o script por
meio do Bash:

```bash
bash bootstrap.sh
```

Durante a primeira execução, o download e a instalação das dependências podem
levar alguns minutos. Não interrompa o processo enquanto houver comandos em
andamento.

#### 6. Confirme a conclusão

A execução foi concluída corretamente quando o terminal exibir:

```text
Bootstrap do user-service concluído com sucesso.
```

Se uma mensagem iniciada por `Erro:` for exibida, corrija o pré-requisito
indicado e execute novamente o Passo 5. O script foi preparado para poder ser
executado mais de uma vez sem duplicar os usuários de demonstração.

Depois da conclusão do bootstrap, volte à raiz do monorepo e inicie o serviço:

```bash
cd ../..
docker compose up -d user-service
docker compose ps user-service
```

### O que o bootstrap executa

Durante a execução, o `bootstrap.sh`:

1. Valida o diretório de execução e a disponibilidade do Python 3.11
2. Cria o ambiente virtual `.venv`, caso ele ainda não exista, e o ativa
3. Atualiza o `pip` e instala as dependências de `requirements.txt`
4. Gera o par de chaves RSA de 2048 bits utilizado pelos tokens JWT, caso as
   chaves ainda não existam
5. Cria o arquivo `.env` com a configuração local padrão, caso ele ainda não
   exista
6. Valida a disponibilidade dos clientes `mysql` e `mysqladmin`
7. Aguarda o MySQL aceitar conexões
8. Cria o banco `users` e o usuário `user_service`, caso ainda não existam
9. Inicializa e configura o Alembic quando sua estrutura ainda não existe
10. Gera a migration inicial caso `alembic/versions` não contenha migrations
11. Executa `alembic upgrade head` para atualizar o schema do banco
12. Cria os usuários de demonstração e o administrador local que ainda não
    estiverem cadastrados

<!-- TODO: Incluir no bootstrap a preparação dos recursos de persistência do
user-service no OCI NoSQL e a carga dos usuários de demonstração quando esse
provider estiver selecionado. -->

### Configuração local criada

Quando o `.env` não existe, o script o cria com:

- Persistência via SQLAlchemy no banco MySQL `users`
- Conexão local pela porta `13306` com o usuário `user_service`
- Mensageria via RabbitMQ em `127.0.0.1:5672`
- Fila de notificações chamada `notifications`
- Emissor JWT `user-service` e audiência `oci-pizza`

<!-- TODO: Adicionar ao .env as configurações locais necessárias para selecionar
e conectar o provider de persistência OCI NoSQL. -->

Se o `.env` já existir, seu conteúdo é preservado sem alterações. Portanto,
confirme se a `DATABASE_URL` existente aponta para o MySQL esperado antes de
executar o bootstrap.

## Reconstruir a imagem Docker

Quando algum arquivo do `user-service` for modificado, reconstrua a imagem
Docker para que as alterações sejam copiadas para o container.

Execute o comando abaixo a partir da raiz do monorepo:

```bash
docker compose build --no-cache user-service
```

A opção `--no-cache` força a reconstrução completa da imagem, sem reutilizar
camadas geradas anteriormente.

Após a conclusão do build, recrie o container para iniciar o serviço com a nova
imagem:

```bash
docker compose up -d user-service
```

Verifique se o serviço voltou a executar:

```bash
docker compose ps user-service
```

## Migrações do banco de dados

O `user-service` utiliza o Alembic para versionar e aplicar alterações no schema
do banco. As migrations fazem parte do código-fonte do serviço e devem ser
versionadas no repositório Git.

O bootstrap inicializa o Alembic somente quando `alembic.ini` ou
`alembic/env.py` não são encontrados. Quando não existe nenhum arquivo Python
em `alembic/versions`, ele cria a migration inicial com autogenerate. Em todas
as execuções, o comando abaixo é aplicado:

```bash
alembic upgrade head
```

Alterações futuras nos modelos ORM devem gerar uma nova migration, em vez de
alterar migrations já aplicadas:

```bash
source .venv/bin/activate
alembic revision --autogenerate -m "descreva a alteração"
alembic upgrade head
```

Revise sempre a migration gerada automaticamente antes de aplicá-la.

<!-- TODO: Documentar e automatizar o versionamento e a evolução das tabelas e
dos índices utilizados pelo user-service, considerando que o Alembic se aplica
somente ao provider SQLAlchemy. -->

## Logging

O logging é configurado durante a inicialização da aplicação:

- Em `development`, os logs são enviados para `stdout`.
- Nos demais ambientes, os logs são enviados ao OCI Logging pela Logging
  Ingestion API, com autenticação via Instance Principal.
- Fora de `development`, `OCI_LOG_ID` é obrigatório e deve conter o OCID do
  Custom Log utilizado para ingestão.
- `LOG_LEVEL` define o nível global dos logs e utiliza `INFO` como padrão.

Os registros enviados ao OCI Logging identificam o `user-service` como origem.

## Usuários de demonstração

O bootstrap inclui os seguintes usuários para demonstrações e testes locais:

| Nome | E-mail | E-mail confirmado | Administrador | Senha local |
| --- | --- | --- | --- | --- |
| Administrador | `admin@ocipizza.com.br` | Sim | Sim | `AdminPassword123!` |
| Maria Oliveira | `maria.oliveira@example.com` | Sim | Não | `DemoPassword123!` |
| Joao Silva | `joao.silva@example.com` | Não | Não | `DemoPassword123!` |
| Rita de Cássia | `rita.cassia@example.com` | Sim | Não | `DemoPassword123!` |

As senhas são persistidas como hash, usando o mesmo serviço de senha da
aplicação.

O processo é idempotente: antes de inserir cada registro, o script procura um
usuário com o mesmo e-mail. Assim, novas execuções não duplicam os usuários de
demonstração.

## Como utilizar a API de usuários

Antes de utilizar a API, confirme que o `user-service` está em execução:

```bash
docker compose ps user-service
```

### Operações CRUD de usuários

CRUD é o conjunto das quatro operações básicas realizadas sobre usuários:
criação (Create), consulta (Read), atualização (Update) e exclusão (Delete).
As rotas públicas e do usuário autenticado implementam criação, consulta e
atualização do próprio perfil. Não existe uma rota para o usuário excluir a
própria conta.

| Operação | Método HTTP | Endpoint | Acesso |
| --- | --- | --- | --- |
| CREATE | `POST` | `/users` | Público. |
| READ | `GET` | `/users/me` | Usuário autenticado. |
| UPDATE | `PUT` | `/users/me` | Usuário autenticado. |
| DELETE | — | — | Não disponível para o próprio usuário. |

#### CREATE — Criar um usuário

Para cadastrar um novo usuário, execute:

```bash
curl --request POST \
  --url http://localhost:8002/users \
  --header 'Content-Type: application/json' \
  --data '{
    "full_name": "Ana Laura",
    "email": "ana.laura@example.com",
    "whatsapp": "11966666666",
    "password": "LocalPassword123!"
  }'
```

Os campos enviados são:

| Campo | Descrição |
| --- | --- |
| `full_name` | Nome completo do novo usuário. |
| `email` | E-mail válido e ainda não cadastrado. |
| `whatsapp` | Número do WhatsApp com DDD, contendo exatamente 11 caracteres. |
| `password` | Senha do usuário, enviada apenas na criação. |

Quando o cadastro for concluído, a API responderá com o status HTTP `201`
(`Created`) e os dados públicos do usuário no padrão JSend. A senha não é
devolvida na resposta.

O e-mail e o WhatsApp devem ser únicos. Se o mesmo comando for executado
novamente, a API responderá com o status HTTP `409 Conflict`, pois o usuário já
estará cadastrado.

#### READ — Consultar o usuário atual

Para consultar os dados do usuário atual, execute:

```bash
curl --request GET \
  --url http://localhost:8002/users/me \
  --header 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx.yyyyy' \
  --header 'Accept: application/json'
```

Substitua o token apresentado no exemplo por um token JWT válido. O identificador
do usuário atual é um UUID obtido a partir da identidade autenticada.

Não é necessário enviar nenhum UUID como parâmetro na URL, pois a rota
`/users/me` identifica o usuário atual por meio da dependência de autenticação.

Quando a consulta for concluída, a API responderá com o status HTTP `200 OK`
e os dados públicos do usuário no padrão JSend. Se o usuário não for
encontrado, a resposta terá o status HTTP `404 Not Found`.

#### UPDATE — Atualizar o WhatsApp do usuário atual

Para atualizar o número de WhatsApp do usuário atual, execute:

```bash
curl --request PUT \
  --url http://localhost:8002/users/me \
  --header 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx.yyyyy' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "whatsapp": "11966666666"
  }'
```

Substitua o token apresentado no exemplo por um token JWT válido. O payload
aceita somente o campo `whatsapp`, que deve conter exatamente 11 caracteres.
O UUID do usuário não deve ser enviado na URL nem no corpo da requisição, pois
é obtido por meio da identidade autenticada.

| Campo | Descrição |
| --- | --- |
| `whatsapp` | Novo número de WhatsApp do usuário, contendo exatamente 11 caracteres. |

Quando a atualização for concluída, a API responderá com o status HTTP `200 OK`
e os dados públicos atualizados do usuário no padrão JSend. Se o usuário não
for encontrado, a resposta terá o status HTTP `404 Not Found`. Um WhatsApp já
cadastrado resulta em `409 Conflict`. Outras falhas de atualização resultam em
`500 Internal Server Error`.

### Endereços do usuário

As operações abaixo permitem ao usuário autenticado gerenciar seus próprios
endereços de entrega. Todas exigem um access token JWT válido no cabeçalho
`Authorization`. O UUID do usuário é obtido a partir do token e não deve ser
informado na URL nem no corpo da requisição.

| Operação | Método HTTP | Endpoint |
| --- | --- | --- |
| Listar endereços | `GET` | `/users/me/addresses` |
| Consultar um endereço | `GET` | `/users/me/addresses/{address_id}` |
| Cadastrar um endereço | `POST` | `/users/me/addresses` |
| Atualizar um endereço | `PUT` | `/users/me/addresses/{address_id}` |
| Excluir um endereço | `DELETE` | `/users/me/addresses/{address_id}` |
| Definir o endereço padrão | `PATCH` | `/users/me/addresses/{address_id}/default` |

Cada usuário pode possuir no máximo três endereços. O primeiro endereço
cadastrado é definido automaticamente como padrão. Quando outro endereço é
definido como padrão, a marcação é removida dos demais.

#### READ — Listar os endereços do usuário autenticado

Para listar os endereços, execute:

```bash
curl --request GET \
  --url http://localhost:8002/users/me/addresses \
  --header 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx.yyyyy' \
  --header 'Accept: application/json'
```

Substitua o token apresentado no exemplo por um access token JWT válido. O
campo `data.addresses` será uma lista vazia quando não houver endereços
cadastrados.

Quando a consulta for concluída, a API responderá com o status HTTP `200 OK` e
os endereços no campo `data.addresses` do padrão JSend:

```json
{
  "status": "success",
  "data": {
    "addresses": [
      {
        "id": "5cd4cc45-7ef7-4478-a048-e297b3570c86",
        "label": "Casa",
        "zip_code": "01310-100",
        "street": "Avenida Paulista",
        "number": "1000",
        "complement": "Apartamento 101",
        "neighborhood": "Bela Vista",
        "city": "São Paulo",
        "state": "SP",
        "is_default": true,
        "created_at": "2026-10-08T18:00:00",
        "updated_at": "2026-10-08T18:00:00"
      }
    ]
  }
}
```

#### READ — Consultar um endereço

Para consultar um endereço pertencente ao usuário autenticado, execute:

```bash
curl --request GET \
  --url http://localhost:8002/users/me/addresses/5cd4cc45-7ef7-4478-a048-e297b3570c86 \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

A API responderá com `200 OK` e o endereço no campo `data.address`. Quando o
UUID não identificar um endereço pertencente ao usuário autenticado, a resposta
será `404 Not Found`, com o código `USER_ADDRESS_NOT_FOUND`.

#### CREATE — Cadastrar um endereço

Para cadastrar um endereço, execute:

```bash
curl --request POST \
  --url http://localhost:8002/users/me/addresses \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "label": "Casa",
    "zip_code": "01310-100",
    "street": "Avenida Paulista",
    "number": "1000",
    "complement": "Apartamento 101",
    "neighborhood": "Bela Vista",
    "city": "São Paulo",
    "state": "SP",
    "is_default": true
  }'
```

Os campos aceitos são:

| Campo | Obrigatório | Descrição |
| --- | --- | --- |
| `label` | Não | Identificação do endereço, com até 50 caracteres. |
| `zip_code` | Sim | CEP contendo entre 8 e 9 caracteres. |
| `street` | Sim | Logradouro contendo até 255 caracteres. |
| `number` | Sim | Número do endereço, com até 20 caracteres. |
| `complement` | Não | Complemento contendo até 100 caracteres. |
| `neighborhood` | Sim | Bairro contendo até 100 caracteres. |
| `city` | Sim | Cidade contendo até 100 caracteres. |
| `state` | Sim | Estado aceito pelo schema com 2 a 30 caracteres e armazenado em letras maiúsculas. |
| `is_default` | Não | Define o endereço como padrão; o valor padrão é `false`. |

Quando o cadastro for concluído, a API responderá com `201 Created` e o
endereço no campo `data.address`. Ao atingir o limite de três endereços, a
resposta será `409 Conflict`, com o código `USER_ADDRESS_LIMIT_EXCEEDED`.

#### UPDATE — Atualizar um endereço

Todos os campos do payload de atualização são opcionais. Somente os campos
enviados serão alterados:

```bash
curl --request PUT \
  --url http://localhost:8002/users/me/addresses/5cd4cc45-7ef7-4478-a048-e297b3570c86 \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "label": "Trabalho",
    "number": "1200",
    "is_default": true
  }'
```

Os limites dos campos são os mesmos utilizados no cadastro, exceto `state`,
que na atualização deve conter exatamente dois caracteres. A API responderá
com `200 OK` e o endereço atualizado em `data.address`. Um endereço inexistente
ou pertencente a outro usuário resulta em `404 Not Found`, com o código
`USER_ADDRESS_NOT_FOUND`.

#### DELETE — Excluir um endereço

Para remover um endereço pertencente ao usuário autenticado, execute:

```bash
curl --request DELETE \
  --url http://localhost:8002/users/me/addresses/5cd4cc45-7ef7-4478-a048-e297b3570c86 \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

Quando a exclusão for concluída, a API responderá com `200 OK` e a mensagem
`User address deleted successfully.`. Um endereço inexistente ou pertencente a
outro usuário resulta em `404 Not Found`, com o código
`USER_ADDRESS_NOT_FOUND`.

#### Definir um endereço como padrão

Para definir um endereço como padrão, execute:

```bash
curl --request PATCH \
  --url http://localhost:8002/users/me/addresses/5cd4cc45-7ef7-4478-a048-e297b3570c86/default \
  --header 'Authorization: Bearer ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

A operação não recebe corpo. A API responderá com `200 OK`, retornando o
endereço em `data.address` com `is_default` igual a `true`. A marcação de
padrão será removida dos demais endereços. Um endereço inexistente ou
pertencente a outro usuário resulta em `404 Not Found`, com o código
`USER_ADDRESS_NOT_FOUND`.

Em todas as operações, a API responderá com `401 Unauthorized` quando o access
token estiver ausente, inválido ou expirado. Payloads ou UUIDs inválidos
resultam em `400 Bad Request` com o código `USER_VALIDATION_ERROR`. Falhas
inesperadas resultam em `500 Internal Server Error`.

### Autenticação do usuário

A autenticação valida o e-mail e a senha de um usuário com o cadastro
confirmado. Quando as credenciais são válidas, a API emite um access token JWT
e um refresh token para a sessão.

Para autenticar um usuário, execute:

```bash
curl --request POST \
  --url http://localhost:8002/auth/login \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "maria.oliveira@example.com",
    "password": "DemoPassword123!"
  }'
```

Os campos enviados são:

| Campo | Descrição |
| --- | --- |
| `email` | Endereço de e-mail associado ao cadastro do usuário. |
| `password` | Senha utilizada para validar as credenciais do usuário. |

Quando a autenticação for concluída, a API responderá com o status HTTP
`200 OK` e os tokens da sessão no padrão JSend:

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx.yyyyy",
    "refresh_token": "REFRESH_TOKEN",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

O `access_token` possui validade de 15 minutos no ambiente local e deve ser
enviado no cabeçalho `Authorization` das operações autenticadas:

```http
Authorization: Bearer <access_token>
```

O `refresh_token` permite solicitar futuramente um novo access token sem
informar novamente o e-mail e a senha. Ele não deve ser enviado no cabeçalho
das requisições autenticadas nem exposto em logs.

> Estado atual: as rotas `/auth/refresh` e `/auth/logout` ainda não estão
> implementadas. Além disso, o schema de login aceita senhas com exatamente 11
> caracteres, enquanto as contas criadas pelo bootstrap utilizam senhas mais
> longas. Portanto, o exemplo de login com uma conta de demonstração somente
> funcionará após a correção dessa validação no código.

A API responderá com `401 Unauthorized` quando o e-mail ou a senha forem
inválidos, com `403 Forbidden` quando o e-mail do usuário ainda não estiver
confirmado e com `500 Internal Server Error` quando não for possível concluir
a autenticação.

### Confirmação do cadastro do usuário

Após o cadastro, o usuário recebe por e-mail um token temporário para confirmar
seu endereço de e-mail. Essa operação é pública e não exige um token de
autenticação Bearer.

Para confirmar o cadastro, execute:

```bash
curl --request POST \
  --url http://localhost:8002/users/confirm \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "ana.laura@example.com",
    "token": "TOKEN_RECEBIDO_POR_EMAIL"
  }'
```

Os campos enviados são:

| Campo | Descrição |
| --- | --- |
| `email` | Endereço de e-mail associado ao cadastro do usuário. |
| `token` | Token temporário recebido no e-mail de confirmação do cadastro. |

O token é válido por 24 horas, pertence ao usuário associado ao e-mail
informado e pode ser utilizado somente uma vez. A API rejeita tokens
inexistentes, expirados, utilizados anteriormente, revogados ou pertencentes a
outro usuário. O token original não é armazenado no banco de dados; somente seu
hash é persistido.

Quando a confirmação for concluída, o campo `confirmed` do usuário será alterado
para `True`, o token será marcado como utilizado e a API responderá com o status
HTTP `200 OK` e a mensagem `User confirmed successfully.` no padrão JSend.
Caso o cadastro já tenha sido confirmado anteriormente, o usuário não será
alterado novamente, mas o token válido apresentado será consumido.

O consumo do token é atômico. Se duas requisições simultâneas tentarem utilizar
o mesmo token, somente uma delas concluirá a confirmação; a outra receberá
`400 Bad Request`, pois o token não estará mais disponível.

A API responderá com `400 Bad Request` quando o usuário não for encontrado ou
quando o token não puder ser validado. Falhas internas durante a consulta ou a
persistência dos dados resultarão em `500 Internal Server Error`.

### Troca de senha do usuário

A troca de senha somente é permitida quando o usuário possui o e-mail
confirmado, ou seja, quando o campo `confirmed` possui o valor `True`. A
operação também exige a senha atual e a confirmação da nova senha. Para alterar
a senha do usuário autenticado, execute:

```bash
curl --request PUT \
  --url http://localhost:8002/users/me/password \
  --header 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx.yyyyy' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "current_password": "DemoPassword123!",
    "new_password": "NewDemoPassword123!",
    "confirm_new_password": "NewDemoPassword123!"
  }'
```

Substitua o token apresentado no exemplo por um token JWT válido. O UUID do
usuário não deve ser enviado na URL nem no corpo da requisição, pois é obtido
por meio da identidade autenticada.

Os campos enviados são:

| Campo | Descrição |
| --- | --- |
| `current_password` | Senha atual, utilizada para validar o usuário. |
| `new_password` | Nova senha que será associada ao usuário. |
| `confirm_new_password` | Confirmação da nova senha; deve possuir o mesmo valor de `new_password`. |

Antes de persistir a alteração, o serviço valida se a senha atual corresponde
ao hash armazenado e se a nova senha coincide com sua confirmação. A nova senha
é armazenada como hash, nunca em texto puro.

Quando a troca for concluída, a API responderá com o status HTTP `200 OK` e a
mensagem `Password updated successfully.` no padrão JSend. A API responderá com
`400 Bad Request` quando a senha atual for inválida ou a confirmação for
diferente da nova senha ou quando o usuário não for encontrado, com
`403 Forbidden` quando o e-mail do usuário não estiver confirmado e com
`500 Internal Server Error` quando não for possível concluir a alteração.

### Redefinição de senha

O fluxo de redefinição permite que o usuário defina uma nova senha sem informar
a senha atual. O processo é composto por duas etapas:

| Etapa | Método HTTP | Endpoint |
| --- | --- | --- |
| Solicitar o token | `POST` | `/users/password-reset/request` |
| Confirmar a nova senha | `POST` | `/users/password-reset/confirm` |

As duas operações são públicas e não exigem um token de autenticação Bearer.

#### Solicitar o token de redefinição

A solicitação de redefinição de senha inicia o fluxo de recuperação de acesso
à conta. Essa operação não exige autenticação, pois é destinada ao usuário que
não consegue acessar sua conta com a senha atual.

Para solicitar a redefinição, execute:

```bash
curl --request POST \
  --url http://localhost:8002/users/password-reset/request \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "maria.oliveira@example.com"
  }'
```

O payload aceita somente o campo abaixo:

| Campo | Descrição |
| --- | --- |
| `email` | Endereço de e-mail válido associado à conta do usuário. |

Quando a conta existe, o e-mail precisa estar confirmado para que o fluxo seja
iniciado.

O serviço gera um token temporário com validade de uma hora, persiste somente
seu hash e publica uma mensagem para que o `notification-service` envie o token
ao e-mail associado à conta. O token original não é armazenado no banco de dados.

Por segurança, a API não informa se um e-mail inexistente está ou não cadastrado.
Tanto para uma solicitação iniciada quanto para um e-mail inexistente, a resposta
possui o status HTTP `200 OK` e a mensagem `Password reset request received.` no
padrão JSend.

A API responderá com `403 Forbidden` quando a conta existir, mas o e-mail ainda
não estiver confirmado, e com `500 Internal Server Error` quando não for possível
persistir o token ou publicar a solicitação de envio do e-mail.

#### Confirmar a redefinição de senha

Após receber o token por e-mail, utilize-o para definir uma nova senha:

```bash
curl --request POST \
  --url http://localhost:8002/users/password-reset/confirm \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "token": "TOKEN_RECEBIDO_POR_EMAIL",
    "new_password": "NewDemoPassword123!",
    "confirm_new_password": "NewDemoPassword123!"
  }'
```

Os campos enviados são:

| Campo | Descrição |
| --- | --- |
| `token` | Token temporário recebido no e-mail de redefinição de senha. |
| `new_password` | Nova senha que será associada ao usuário. |
| `confirm_new_password` | Confirmação da nova senha; deve possuir o mesmo valor de `new_password`. |

O token é válido por uma hora e pode ser utilizado somente uma vez. A API
rejeita tokens inexistentes, expirados, utilizados anteriormente ou revogados.
Quando o token é aceito, a nova senha é armazenada como hash e o token é
marcado como utilizado, impedindo sua reutilização.

Quando a redefinição for concluída, a API responderá com o status HTTP `200 OK`
e a mensagem `Password reset successfully.` no padrão JSend. A API responderá
com `400 Bad Request` quando a confirmação da senha for diferente da nova senha
ou quando o token for inválido, expirado, utilizado ou revogado. O mesmo status
`400 Bad Request` é retornado quando o usuário associado ao token não é
encontrado. Falhas internas resultam em `500 Internal Server Error`.

### Endpoints operacionais

O serviço expõe dois endpoints públicos utilizados para verificação de saúde
e validação dos access tokens:

| Finalidade | Método HTTP | Endpoint |
| --- | --- | --- |
| Verificar se o serviço está ativo | `GET` | `/health` |
| Consultar as chaves públicas JWT | `GET` | `/.well-known/jwks.json` |

Para verificar o serviço localmente, execute:

```bash
curl --request GET \
  --url http://localhost:8002/health \
  --header 'Accept: application/json'
```

O endpoint JWKS retorna o conjunto de chaves públicas utilizado pelos demais
serviços para validar a assinatura dos access tokens emitidos pelo
`user-service`.

### Operações administrativas

As operações administrativas permitem gerenciar qualquer usuário da
aplicação, tanto contas administrativas quanto contas sem privilégios
administrativos. Todas exigem um access token JWT cuja claim `is_admin` possua
o valor `true`. O campo ou filtro `is_admin` determina o tipo da conta que será
criada, atualizada ou consultada.

#### Administração de usuários

| Operação | Método HTTP | Endpoint |
| --- | --- | --- |
| Criar usuário | `POST` | `/admin/users` |
| Listar usuários | `GET` | `/admin/users` |
| Listar usuários pela rota administrativa legada | `GET` | `/users` |
| Consultar usuário | `GET` | `/admin/users/{user_id}` |
| Atualizar usuário | `PUT` | `/admin/users/{user_id}` |
| Definir senha | `PUT` | `/admin/users/{user_id}/password` |
| Confirmar cadastro | `POST` | `/admin/users/{user_id}/confirm` |
| Revogar sessões | `POST` | `/admin/users/{user_id}/revoke-sessions` |
| Excluir usuário | `DELETE` | `/admin/users/{user_id}` |

Substitua `ADMIN_ACCESS_TOKEN` pelo access token de um administrador e
`USER_ID` pelo UUID do usuário correspondente nos exemplos abaixo.

##### Criar um usuário

```bash
curl --request POST \
  --url http://localhost:8002/admin/users \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "full_name": "Juliana Martins",
    "email": "juliana.martins@example.com",
    "whatsapp": "11955555555",
    "password": "LocalPassword123!",
    "confirmed": true,
    "is_admin": false
  }'
```

| Campo | Descrição |
| --- | --- |
| `full_name` | Nome completo do usuário. |
| `email` | Endereço de e-mail único do usuário. |
| `whatsapp` | Número de WhatsApp único do usuário. |
| `password` | Senha inicial do usuário. |
| `confirmed` | Indica se o e-mail deve ser criado como confirmado; o padrão é `false`. |
| `is_admin` | Indica se o usuário possuirá privilégios administrativos; o padrão é `false`. |

Quando `confirmed` for `false`, o serviço inicia o fluxo de envio do e-mail de
confirmação. A criação retorna `201 Created`; e-mail ou WhatsApp duplicado
resulta em `409 Conflict`.

##### Listar usuários

```bash
curl --request GET \
  --url 'http://localhost:8002/admin/users?email=example.com&confirmed=true&is_admin=false&limit=50&offset=0' \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

Os filtros `email`, `confirmed` e `is_admin` são opcionais. `limit` possui o
valor padrão `50` e `offset`, o valor padrão `0`. A resposta `200 OK` retorna
os registros no campo `data.users`, ordenados do mais recente para o mais
antigo.

| Campo | Descrição |
| --- | --- |
| `email` | Filtra por parte do endereço de e-mail, sem diferenciar letras maiúsculas e minúsculas. |
| `confirmed` | Filtra pelo estado de confirmação do e-mail; aceita `true` ou `false`. |
| `is_admin` | Filtra pela presença de privilégios administrativos; aceita `true` ou `false`. |
| `limit` | Define a quantidade máxima de usuários retornados; o padrão é `50`. |
| `offset` | Define a quantidade de registros ignorados antes do retorno; o padrão é `0`. |

##### Listar usuários pela rota administrativa `/users`

A rota `GET /users` também é administrativa e oferece os mesmos filtros de
listagem. Ela exige a claim `is_admin` igual a `true`, apesar de não utilizar o
prefixo `/admin`:

```bash
curl --request GET \
  --url 'http://localhost:8002/users?email=example.com&confirmed=true&is_admin=false&limit=50&offset=0' \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

Os parâmetros `email`, `confirmed`, `is_admin`, `limit` e `offset` possuem o
mesmo comportamento descrito para `GET /admin/users`. A resposta `200 OK`
retorna os registros em `data.users`; quando nenhum registro atender aos
filtros, esse campo será uma lista vazia.

##### Consultar um usuário

```bash
curl --request GET \
  --url http://localhost:8002/admin/users/USER_ID \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

A resposta `200 OK` retorna o usuário no campo `data.user`. Um UUID sem usuário
correspondente resulta em `404 Not Found`.

| Campo | Descrição |
| --- | --- |
| `user_id` | UUID do usuário que será consultado, informado no caminho da requisição. |

##### Atualizar um usuário

```bash
curl --request PUT \
  --url http://localhost:8002/admin/users/USER_ID \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "full_name": "Juliana Martins",
    "email": "juliana.martins@example.com",
    "whatsapp": "11944444444",
    "confirmed": true,
    "is_admin": false
  }'
```

Todos os campos do payload são obrigatórios. A operação permite alterar nome,
e-mail, WhatsApp, estado de confirmação e privilégio administrativo. A resposta
de sucesso é `200 OK`; usuário inexistente resulta em `404 Not Found` e e-mail
ou WhatsApp duplicado resulta em `409 Conflict`.

| Campo | Descrição |
| --- | --- |
| `user_id` | UUID do usuário que será atualizado, informado no caminho da requisição. |
| `full_name` | Nome completo do usuário. |
| `email` | Endereço de e-mail único do usuário. |
| `whatsapp` | Número de WhatsApp único do usuário. |
| `confirmed` | Indica se o endereço de e-mail do usuário está confirmado. |
| `is_admin` | Indica se o usuário possui privilégios administrativos. |

##### Definir a senha de um usuário

```bash
curl --request PUT \
  --url http://localhost:8002/admin/users/USER_ID/password \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "new_password": "NewPassword123!",
    "confirm_new_password": "NewPassword123!"
  }'
```

A operação não exige a senha atual do usuário. A nova senha e sua confirmação
devem ser iguais e possuir entre 8 e 20 caracteres. O sucesso retorna `200 OK`
e a mensagem `User password updated successfully.`. Confirmação divergente
resulta em `400 Bad Request` e usuário inexistente, em `404 Not Found`.

##### Confirmar o cadastro de um usuário

```bash
curl --request POST \
  --url http://localhost:8002/admin/users/USER_ID/confirm \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

Essa operação confirma o cadastro sem exigir o token enviado por e-mail e
retorna os dados atualizados em `data.user`. Usuário inexistente resulta em
`404 Not Found`.

| Campo | Descrição |
| --- | --- |
| `user_id` | UUID do usuário cujo cadastro será confirmado, informado no caminho da requisição. |

##### Revogar as sessões de um usuário

```bash
curl --request POST \
  --url http://localhost:8002/admin/users/USER_ID/revoke-sessions \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

A operação revoga todos os refresh tokens ativos do usuário, impedindo que
essas sessões renovem seus access tokens. O sucesso retorna `200 OK` e a mensagem
`User sessions revoked successfully.`.

| Campo | Descrição |
| --- | --- |
| `user_id` | UUID do usuário cujas sessões serão revogadas, informado no caminho da requisição. |

##### Excluir um usuário

```bash
curl --request DELETE \
  --url http://localhost:8002/admin/users/USER_ID \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

A exclusão remove o usuário e seus registros relacionados configurados com
`ON DELETE CASCADE`. O sucesso retorna `200 OK` e a mensagem
`User deleted successfully.`; usuário inexistente resulta em `404 Not Found`.

| Campo | Descrição |
| --- | --- |
| `user_id` | UUID do usuário que será excluído, informado no caminho da requisição. |

#### Administração dos endereços de um usuário

As rotas administrativas de endereços podem atuar sobre contas
administrativas ou não administrativas. `USER_ID` identifica o proprietário do
endereço e `ADDRESS_ID`, o endereço que será alterado.

| Operação | Método HTTP | Endpoint |
| --- | --- | --- |
| Listar endereços | `GET` | `/admin/users/{user_id}/addresses` |
| Cadastrar endereço | `POST` | `/admin/users/{user_id}/addresses` |
| Atualizar endereço | `PUT` | `/admin/users/{user_id}/addresses/{address_id}` |
| Excluir endereço | `DELETE` | `/admin/users/{user_id}/addresses/{address_id}` |
| Definir endereço padrão | `PATCH` | `/admin/users/{user_id}/addresses/{address_id}/default` |

Cada usuário pode possuir no máximo três endereços. O primeiro endereço
é definido automaticamente como padrão. Quando outro endereço é marcado
como padrão, essa marcação é removida dos demais.

##### Listar os endereços de um usuário

```bash
curl --request GET \
  --url http://localhost:8002/admin/users/USER_ID/addresses \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

A resposta `200 OK` retorna a lista em `data.addresses`. Quando o usuário não
possuir endereços, o campo será uma lista vazia.

##### Cadastrar um endereço para um usuário

```bash
curl --request POST \
  --url http://localhost:8002/admin/users/USER_ID/addresses \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "label": "Casa",
    "zip_code": "01310-100",
    "street": "Avenida Paulista",
    "number": "1000",
    "complement": "Apartamento 101",
    "neighborhood": "Bela Vista",
    "city": "São Paulo",
    "state": "SP",
    "is_default": true
  }'
```

| Campo | Obrigatório | Descrição |
| --- | --- | --- |
| `label` | Não | Identificação do endereço, com até 50 caracteres. |
| `zip_code` | Sim | CEP contendo entre 8 e 9 caracteres. |
| `street` | Sim | Logradouro contendo até 255 caracteres. |
| `number` | Sim | Número contendo até 20 caracteres. |
| `complement` | Não | Complemento contendo até 100 caracteres. |
| `neighborhood` | Sim | Bairro contendo até 100 caracteres. |
| `city` | Sim | Cidade contendo até 100 caracteres. |
| `state` | Sim | Estado contendo entre 2 e 30 caracteres; o valor é armazenado em letras maiúsculas. |
| `is_default` | Não | Define o endereço como padrão; o valor padrão é `false`. |

O sucesso retorna `201 Created` e o endereço em `data.address`. Se o usuário
já possuir três endereços, a API retorna `409 Conflict` com o código
`USER_ADDRESS_LIMIT_EXCEEDED`.

##### Atualizar um endereço de um usuário

```bash
curl --request PUT \
  --url http://localhost:8002/admin/users/USER_ID/addresses/ADDRESS_ID \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "label": "Trabalho",
    "number": "1200",
    "is_default": true
  }'
```

Todos os campos do payload são opcionais e somente os campos enviados são
alterados. Os limites são os mesmos do cadastro, exceto `state`, que deve conter
exatamente dois caracteres na atualização. O sucesso retorna `200 OK` e o
endereço atualizado em `data.address`.

##### Excluir um endereço de um usuário

```bash
curl --request DELETE \
  --url http://localhost:8002/admin/users/USER_ID/addresses/ADDRESS_ID \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

O sucesso retorna `200 OK` e a mensagem
`User address deleted successfully.`. Um endereço inexistente ou que não
pertença ao usuário informado retorna `404 Not Found` com o código
`USER_ADDRESS_NOT_FOUND`.

##### Definir o endereço padrão de um usuário

```bash
curl --request PATCH \
  --url http://localhost:8002/admin/users/USER_ID/addresses/ADDRESS_ID/default \
  --header 'Authorization: Bearer ADMIN_ACCESS_TOKEN' \
  --header 'Accept: application/json'
```

A operação não recebe corpo. O sucesso retorna `200 OK` e o endereço em
`data.address`, com `is_default` igual a `true`. Um endereço inexistente ou que
não pertença ao usuário informado retorna `404 Not Found` com o código
`USER_ADDRESS_NOT_FOUND`.

Para todas as operações administrativas, um access token ausente, inválido ou
expirado resulta em `401 Unauthorized`, enquanto um usuário sem privilégios
administrativos recebe `403 Forbidden`. Falhas internas de persistência ou
consulta resultam em `500 Internal Server Error`.

## Códigos HTTP

| Status | Uso |
| --- | --- |
| `200 OK` | Consultas, atualizações, autenticação e operações administrativas concluídas. |
| `201 Created` | Usuário criado. |
| `400 Bad Request` | Payload, parâmetro, token de confirmação ou regra de senha inválida. |
| `401 Unauthorized` | Access token ausente, inválido ou expirado, ou credenciais de autenticação inválidas. |
| `403 Forbidden` | Usuário sem privilégio administrativo, não confirmado ou sem autorização para a operação. |
| `404 Not Found` | Usuário ou recurso solicitado não encontrado. |
| `409 Conflict` | E-mail ou WhatsApp já utilizado por outro usuário. |
| `500 Internal Server Error` | Falha interna de persistência, mensageria, consulta ou processamento. |
