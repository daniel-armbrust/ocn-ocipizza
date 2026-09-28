# User Service

O `user-service` é responsável pelo gerenciamento de usuários e dados de perfil
da aplicação OCI Pizza. Para preparar o serviço em um ambiente local de
desenvolvimento, utilize o script `bootstrap.sh`.

## Dependências do serviço

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
4. Cria o arquivo `.env` com a configuração local padrão, caso ele ainda não
   exista
5. Valida a disponibilidade dos clientes `mysql` e `mysqladmin`
6. Aguarda o MySQL aceitar conexões
7. Cria o banco `users` e o usuário `user_service`, caso ainda não existam
8. Inicializa e configura o Alembic quando sua estrutura ainda não existe
9. Gera a migration inicial caso `alembic/versions` não contenha migrations
10. Executa `alembic upgrade head` para atualizar o schema do banco
11. Cria os usuários de demonstração que ainda não estiverem cadastrados

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

CRUD é o conjunto das quatro operações básicas realizadas sobre usuários:
criação (Create), consulta (Read), atualização (Update) e exclusão (Delete).

| Operação | Método HTTP | Endpoint | Documentação |
| --- | --- | --- | --- |
| CREATE | `POST` | `/users` | Disponível nesta seção. |
| READ | A definir | A definir | Será preenchida posteriormente. |
| UPDATE | A definir | A definir | Será preenchida posteriormente. |
| DELETE | A definir | A definir | Será preenchida posteriormente. |

### CREATE — Criar um usuário

Antes de executar o comando, confirme que o `user-service` está em execução:

```bash
docker compose ps user-service
```

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
