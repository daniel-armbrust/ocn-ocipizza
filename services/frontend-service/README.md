# OCI Pizza — Frontend Service

## Responsabilidade do serviço

O `frontend-service` renderiza a interface web da OCI Pizza com FastAPI,
Jinja2, HTML, CSS e JavaScript. Ele também atua como BFF (Backend For
Frontend), mantendo tokens fora do navegador e intermediando as chamadas aos
microsserviços.

Suas principais responsabilidades são:

- Renderizar o cardápio, o carrinho e as páginas de usuários
- Consultar o catálogo no `pizza-service`
- Intermediar cadastro, autenticação, perfil e endereços no `user-service`
- Validar formulários com WTForms antes de chamar os microsserviços
- Manter access token e refresh token no repositório de sessões do backend
- Enviar ao navegador somente um identificador opaco de sessão em cookie
  `HttpOnly`
- Proteger operações de escrita contra CSRF
- Traduzir códigos funcionais das APIs em mensagens para o usuário

O navegador não acessa diretamente o `user-service` e não recebe os tokens de
autenticação. As chamadas que exigem credenciais são realizadas pelo BFF.

## Dependências do serviço

| Componente | Responsabilidade |
| --- | --- |
| `pizza-service` | Fornece as pizzas exibidas no cardápio. |
| `user-service` | Realiza cadastro, autenticação e operações do perfil e dos endereços. |
| Redis | Provider padrão para armazenamento das sessões opacas do BFF. |

### Dependências Python

As dependências são instaladas pelo arquivo `requirements.txt`.

| Biblioteca | Versão | Uso principal |
| --- | --- | --- |
| FastAPI | 0.141.1 | Rotas do BFF, injeção de dependências e servidor ASGI. |
| HTTPX | 0.28.1 | Chamadas assíncronas ao `pizza-service` e ao `user-service`. |
| Jinja2 | 3.1.6 | Renderização dos templates HTML. |
| pydantic-settings | 2.15.0 | Leitura das configurações de ambiente. |
| WTForms | 3.2.2 | Renderização e validação dos formulários. |
| starlette-wtf | 0.5.0 | Integração da proteção CSRF com Starlette/FastAPI. |
| itsdangerous | 2.2.0 | Assinatura dos tokens utilizados pela proteção CSRF. |
| python-multipart | 0.0.32 | Leitura dos formulários HTML. |
| Redis | 7.0.1 | Acesso assíncrono ao provider padrão de sessões. |
| SQLAlchemy | 2.0.43 | Suporte ao provider relacional alternativo de sessões. |
| Alembic | 1.16.5 | Versionamento do schema do provider relacional. |
| PyMySQL | 1.1.2 | Driver MySQL utilizado pelo provider relacional. |
| OCI SDK | 2.160.3 | Autenticação e integração com serviços da OCI. |
| borneo | 5.4.3 | Acesso ao Oracle NoSQL como provider alternativo de sessões. |

O ambiente de execução utiliza Python 3.11.

## Configurações

As configurações são lidas de variáveis de ambiente e, em desenvolvimento,
podem ser definidas em `.env`.

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `APP_NAME` | Não | Nome da aplicação; padrão `frontend-service`. |
| `APP_ENV` | Não | Ambiente de execução; padrão `development`. |
| `DEBUG` | Não | Ativa recursos de depuração. |
| `PERSISTENCE_PROVIDER` | Não | Provider das sessões; o padrão é `redis`. |
| `REDIS_ENDPOINT` | Para Redis | Endpoint utilizado pelo repositório de sessões. |
| `DATABASE_URL` | Para SQLAlchemy | URL do provider relacional alternativo. |
| `SESSION_COOKIE_NAME` | Não | Nome do cookie opaco; padrão `ocpssid`. |
| `SESSION_TTL` | Não | Limite de duração da sessão em segundos; padrão `86400`. |
| `SESSION_SECRET_KEY` | Sim | Chave utilizada pelo middleware interno de sessão. |
| `CSRF_SECRET_KEY` | Sim | Chave utilizada para assinar e validar tokens CSRF. |
| `PIZZA_SERVICE_URL` | Sim | URL interna do `pizza-service`. |
| `USER_SERVICE_URL` | Sim | URL interna do `user-service`. |
| `HTTP_CLIENT_TIMEOUT` | Não | Timeout das chamadas aos microsserviços; padrão `10.0`. |
| `CHATBOT_CLIENT_TIMEOUT` | Não | Timeout reservado às chamadas do chatbot; padrão `60.0`. |
| `LOG_LEVEL` | Não | Nível de logging; padrão `INFO`. |
| `OCI_LOG_ID` | Fora de desenvolvimento | OCID do Custom Log utilizado pelo OCI Logging. |

No `docker-compose.yaml`, o serviço é publicado em:

```text
http://localhost:8010
```

## Execução local

Com a infraestrutura e os microsserviços disponíveis, execute:

```bash
cd services/frontend-service
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

Também é possível utilizar o script de desenvolvimento:

```bash
cd services/frontend-service
./startdev.sh
```

Para executar pelo Docker Compose a partir da raiz do monorepo:

```bash
docker compose up -d frontend-service
docker compose ps frontend-service
```

## Rotas web

### Navegação e catálogo

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/` | Público | Redireciona para `/pizzas`. |
| `GET` | `/pizzas` | Público | Renderiza o cardápio consultado no `pizza-service`. |
| `GET` | `/cart` | Público | Renderiza o carrinho armazenado no navegador. |

`GET /pizzas` aceita os parâmetros opcionais `category`, `available`, `limit`
e `offset`. O filtro `available` só é encaminhado ao `pizza-service` quando
possui um valor booleano válido.

O menu é montado de acordo com a sessão validada no backend:

| Estado | Itens exibidos |
| --- | --- |
| Visitante | Cardápio, Novo Usuário e Entrar. |
| Autenticado | Cardápio, Meus Dados e Sair. |

O ícone da pizza no menu representa o carrinho e apresenta a quantidade total
de itens armazenados no `localStorage`.

### Cadastro e autenticação

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/users/register` | Público | Exibe o formulário de cadastro. |
| `POST` | `/users/register` | Público | Valida o formulário e cria o usuário pelo `user-service`. |
| `GET` | `/users/login` | Público | Exibe o formulário de autenticação. |
| `POST` | `/users/login` | Público | Autentica o usuário e cria uma sessão opaca no BFF. |
| `POST` | `/users/logout` | Autenticado | Revoga a sessão remota, remove a sessão local e apaga o cookie. |

Após um cadastro bem-sucedido, o usuário é redirecionado para o login com a
mensagem de que o e-mail de confirmação foi enviado. Após o login, o usuário é
redirecionado ao cardápio.

### Perfil do usuário

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/users/profile` | Autenticado | Consulta e exibe os dados pessoais e os endereços. |
| `PUT` | `/users/profile/whatsapp` | Autenticado | Valida e atualiza o WhatsApp pelo `user-service`. |

Nome completo e e-mail são apresentados como campos somente para leitura. O
WhatsApp é renderizado por `UserWhatsappUpdateForm`, recebe a máscara
`(99) 99999-9999` e é normalizado para onze dígitos antes da chamada ao
`user-service`.

A atualização é enviada pelo JavaScript e termina com um redirect para o
perfil. O parâmetro `code` é traduzido por `USER_MESSAGES` e exibido pelo
componente compartilhado de mensagens.

### Endereços do usuário

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/users/profile/addresses/new` | Autenticado | Exibe o formulário de um novo endereço. |
| `POST` | `/users/profile/addresses/new` | Autenticado | Valida e cadastra o endereço pelo `user-service`. |
| `DELETE` | `/users/profile/addresses/{address_id}` | Autenticado | Exclui o endereço selecionado. |

O formulário `UserAddressForm` centraliza atributos HTML, normalização e
validação de identificação, CEP, logradouro, número, complemento, bairro,
cidade, estado e indicação de endereço principal.

No perfil, o usuário pode alternar entre os endereços pelo campo de seleção. O
endereço principal é identificado pelo selo “Principal”. A exclusão exige
confirmação no navegador, envia o token CSRF e redireciona novamente ao perfil
com uma mensagem de sucesso ou erro.

As operações de editar um endereço e definir outro endereço como principal
separadamente ainda não possuem rotas no `frontend-service`.

## Sessões e autenticação BFF

Após a autenticação, access token e refresh token são armazenados somente no
provider de sessões. O cookie enviado ao navegador contém o identificador
opaco definido por `SESSION_COOKIE_NAME` e utiliza:

- `HttpOnly` em todos os ambientes
- `Secure` fora de `development`
- `SameSite=Lax` em desenvolvimento
- `SameSite=Strict` nos demais ambientes

A duração efetiva da sessão é limitada ao menor valor entre `SESSION_TTL` e a
validade do access token. Sessões expiradas ou sem informação confiável de
expiração são removidas e não habilitam os itens autenticados do menu.

## Proteção CSRF

As operações de escrita utilizam `@csrf_protect`. Formulários HTML enviam o
campo oculto `csrf_token`; chamadas JavaScript enviam o mesmo token no
cabeçalho `X-CSRFToken`.

Quando o token CSRF está ausente, inválido ou expirado, o handler global
redireciona a navegação para `/`, evitando que uma resposta JSON interna seja
mostrada ao usuário.

## JavaScript

| Arquivo | Responsabilidade |
| --- | --- |
| `app.js` | Comportamentos globais, mensagens temporárias e carrinho compartilhado. |
| `interaction_lock.js` | Bloqueia a interface durante formulários, chamadas assíncronas e navegações marcadas. |
| `pizza_client.js` | Filtros, imagens e inclusão de pizzas no carrinho. |
| `cart_client.js` | Exibição e manipulação dos itens do carrinho no `localStorage`. |
| `user_auth.js` | Máscara no cadastro e comportamento dos fluxos de autenticação. |
| `user_profile.js` | Máscara e atualização do WhatsApp. |
| `user_address.js` | Seleção e exclusão dos endereços do perfil. |

Durante operações que aguardam resposta do backend, a tela recebe uma camada
visual de processamento e fica temporariamente indisponível para novas ações.

## Carrinho

O carrinho utiliza a chave `ocipizza.cart` no `localStorage`. Cada item mantém
o identificador, nome, preço, URL da imagem e quantidade da pizza. A quantidade
total é exibida no ícone do menu.

Atualmente, o `frontend-service` possui a página `GET /cart`, mas não possui
uma rota de checkout registrada.

## Mensagens e erros

Os códigos funcionais retornados ou adicionados aos redirects são convertidos
em mensagens em português pelos módulos de `app/messages`. O componente
`templates/components/message.html` mantém a apresentação consistente entre
login, cadastro, cardápio, perfil e endereços.

O serviço possui páginas HTML para os erros `404`, `500`, `502` e `503`. O
handler global renderiza `404.html` para rotas inexistentes e `500.html` para
falhas inesperadas. Indisponibilidade do `pizza-service` durante o cardápio
renderiza `503.html`.

## Logging

O logging é configurado durante a inicialização da aplicação:

- Em `development`, os logs são enviados para `stdout`.
- Nos demais ambientes, os logs também são enviados ao OCI Logging.
- Exceções inesperadas são registradas antes da página genérica de erro 500.

## Documentação interativa

Em `development`, o FastAPI disponibiliza:

| Interface | URL local |
| --- | --- |
| Swagger UI | `http://localhost:8010/docs` |
| ReDoc | `http://localhost:8010/redoc` |
| OpenAPI JSON | `http://localhost:8010/openapi.json` |

Fora de `development`, essas três rotas são desabilitadas. As páginas HTML da
aplicação continuam disponíveis conforme as regras de autenticação descritas
acima.
