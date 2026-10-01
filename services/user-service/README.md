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
| MySQL | Armazena usuários, tokens e históricos de senha. |
| RabbitMQ | Publica mensagens assíncronas, como solicitações de envio de e-mail. |

O serviço não acessa diretamente o banco de dados de outro microsserviço. No
Docker Compose, MySQL e RabbitMQ são serviços de infraestrutura independentes e
devem estar disponíveis antes da inicialização do `user-service`.

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
| PyJWT | 2.10.1 | Suporte à criação e validação de tokens JWT. |
| passlib | 1.7.4 | Suporte a mecanismos de proteção de senhas. |
| bcrypt | 4.3.0 | Suporte ao algoritmo de hash bcrypt. |

O ambiente de execução do serviço utiliza Python 3.11. Não instale essas
bibliotecas manualmente uma a uma: o bootstrap realiza a instalação das versões
definidas em `requirements.txt`.

## `bootstrap.sh` — Bootstrap do ambiente local

O script `bootstrap.sh` automatiza a criação do ambiente Python, a configuração do banco de
dados, a execução das migrations e a inclusão dos usuários de demonstração.

> O bootstrap foi desenvolvido exclusivamente para desenvolvimento local. As
> credenciais padrão usadas pelo script não devem ser reutilizadas em ambientes
> de produção.

### Pré-requisitos

Antes de executar o `bootstrap.sh`, suba os serviços necessários usando uma das
alternativas abaixo:

1. execute `make development-infra` para iniciar toda a infraestrutura do
   ambiente de desenvolvimento e, em seguida, execute
   `docker compose up -d user-service` para iniciar o serviço; ou
2. execute `docker compose up -d mysql rabbitmq user-service` para iniciar
   somente os componentes necessários ao desenvolvimento do `user-service`.

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

Após a conclusão do comando, inicie o `user-service`:

```bash
docker compose up -d user-service
```

Para iniciar somente os componentes necessários ao desenvolvimento do
`user-service`, execute:

```bash
docker compose up -d mysql rabbitmq user-service
```

O argumento `-d` executa o container em segundo plano e libera o terminal para
os próximos comandos. Esse comando inicia o banco de dados MySQL, o broker de
mensagens RabbitMQ e o próprio `user-service`.

#### 3. Verifique o estado dos serviços

Execute:

```bash
docker compose ps mysql rabbitmq user-service
```

Na coluna de estado, aguarde até o MySQL e o RabbitMQ aparecerem como
`healthy`. O `user-service` deve aparecer como `Up`. O bootstrap também
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
12. Cria os usuários de demonstração que ainda não estiverem cadastrados

### Configuração local criada

Quando o `.env` não existe, o script o cria com:

- Persistência via SQLAlchemy no banco MySQL `users`
- Conexão local pela porta `13306` com o usuário `user_service`
- Mensageria via RabbitMQ em `127.0.0.1:5672`
- Fila de notificações chamada `notifications`
- Emissor JWT `user-service` e audiência `oci-pizza`

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

## Usuários de demonstração

O bootstrap inclui os seguintes usuários para demonstrações e testes locais:

| Nome | E-mail | E-mail confirmado |
| --- | --- | --- |
| Maria Oliveira | `maria.oliveira@example.com` | Sim |
| Joao Silva | `joao.silva@example.com` | Não |
| Rita de Cássia | `rita.cassia@example.com` | Sim |

Todos utilizam a senha local `DemoPassword123!`. As senhas são persistidas como
hash, usando o mesmo serviço de senha da aplicação.

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

| Operação | Método HTTP | Endpoint | Documentação |
| --- | --- | --- | --- |
| CREATE | `POST` | `/users` | Disponível nesta seção. |
| READ | `GET` | `/users/me` | Disponível nesta seção. |
| UPDATE | `PUT` | `/users/me` | Disponível nesta seção. |
| DELETE | A definir | A definir | Será preenchida posteriormente. |

#### CREATE — Criar um usuário

Para cadastrar um novo usuário, execute:

```bash
curl --request POST \
  --url http://localhost:8002/users \
  --header 'Content-Type: application/json' \
  --data '{
    "full_name": "Ana Laura",
    "email": "ana.laura@example.com",
    "whatsapp": "+5511966666666",
    "password": "LocalPassword123!"
  }'
```

Os campos enviados são:

| Campo | Descrição |
| --- | --- |
| `full_name` | Nome completo do novo usuário. |
| `email` | E-mail válido e ainda não cadastrado. |
| `whatsapp` | Número do WhatsApp com código do país e DDD. |
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

Quando a atualização for concluída, a API responderá com o status HTTP `200 OK`
e os dados públicos atualizados do usuário no padrão JSend. Se o usuário não
for encontrado, a resposta terá o status HTTP `404 Not Found`. Se não for
possível concluir a atualização, a resposta terá o status HTTP
`500 Internal Server Error`.

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

O token é válido por 24 horas e pertence ao usuário associado ao e-mail
informado. A API rejeita tokens inexistentes, expirados, utilizados
anteriormente, revogados ou pertencentes a outro usuário. O token original não
é armazenado no banco de dados; somente seu hash é persistido.

Quando a confirmação for concluída, o campo `confirmed` do usuário será alterado
para `True`, o token será marcado como utilizado e a API responderá com o status
HTTP `200 OK` e a mensagem `User confirmed successfully.` no padrão JSend.

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
diferente da nova senha, com `403 Forbidden` quando o e-mail do usuário não
estiver confirmado, com `404 Not Found` quando o usuário não for encontrado e
com `500 Internal Server Error` quando não for possível concluir a alteração.

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
ou quando o token for inválido, expirado, utilizado ou revogado; com
`404 Not Found` quando o usuário associado ao token não for encontrado; e com
`500 Internal Server Error` quando não for possível concluir a redefinição.
