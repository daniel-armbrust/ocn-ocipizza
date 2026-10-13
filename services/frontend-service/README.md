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
- Consultar elegibilidade, prazo e taxa de entrega no `delivery-service`
- Preparar e revalidar os dados apresentados durante o checkout
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
| `delivery-service` | Verifica a elegibilidade do CEP e fornece prazo e taxa de entrega. |
| `order-service` | Cria pedidos e fornece o histórico do usuário autenticado. |
| Redis | Provider padrão para armazenamento das sessões opacas do BFF. |

### Dependências Python

As dependências são instaladas pelo arquivo `requirements.txt`.

| Biblioteca | Versão | Uso principal |
| --- | --- | --- |
| FastAPI | 0.141.1 | Rotas do BFF, injeção de dependências e servidor ASGI. |
| HTTPX | 0.28.1 | Chamadas assíncronas aos microsserviços consumidos pelo BFF. |
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
| `DELIVERY_SERVICE_URL` | Sim | URL interna do `delivery-service`. |
| `ORDER_SERVICE_URL` | Sim | URL interna do `order-service`. |
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

<!-- TODO: O startdev.sh combina o hostname interno `redis` com a porta
publicada `16379`. Alinhar o endpoint para execução no host antes de considerar
esse fluxo autossuficiente; o .env.example utiliza 127.0.0.1:16379. -->

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
| `POST` | `/cart/checkout` | Autenticado | Prepara e exibe o checkout com dados atuais das APIs. |
| `POST` | `/cart/checkout/confirm` | Autenticado | Revalida o checkout, cria o pedido e redireciona para o cardápio. |
| `GET` | `/health` | Público | Retorna o estado básico do frontend-service. |

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
| `GET` | `/users/confirm` | Público | Confirma o e-mail pelo token e redireciona para o login. |
| `GET` | `/users/login` | Público | Exibe o formulário de autenticação. |
| `POST` | `/users/login` | Público | Autentica o usuário e cria uma sessão opaca no BFF. |
| `POST` | `/users/logout` | Autenticado | Revoga a sessão remota, remove a sessão local e apaga o cookie. |

Após um cadastro bem-sucedido, o usuário é redirecionado para o login com a
mensagem de que o e-mail de confirmação foi enviado. Após o login, o usuário é
redirecionado ao cardápio.

O link de confirmação utiliza `GET /users/confirm?token=...`. O frontend envia
o token ao `user-service` e redireciona para o login, onde o componente global
de mensagens apresenta o resultado da confirmação.

### Perfil do usuário

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/users/profile` | Autenticado | Consulta e exibe os dados pessoais. |
| `PUT` | `/users/profile/whatsapp` | Autenticado | Valida e atualiza o WhatsApp pelo `user-service`. |
| `GET` | `/users/profile/orders` | Autenticado | Consulta e exibe o histórico retornado pelo `order-service`. |

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
| `GET` | `/users/profile/addresses` | Autenticado | Consulta e exibe os endereços cadastrados. |
| `GET` | `/users/profile/addresses/new` | Autenticado | Exibe o formulário de um novo endereço. |
| `POST` | `/users/profile/addresses/new` | Autenticado | Valida e cadastra o endereço pelo `user-service`. |
| `DELETE` | `/users/profile/addresses/{address_id}` | Autenticado | Exclui o endereço selecionado. |

O formulário `UserAddressForm` centraliza atributos HTML, normalização e
validação de identificação, CEP, logradouro, número, complemento, bairro,
cidade, estado e indicação de endereço principal.

O CEP é exibido no formulário com a máscara `99999-999`, mas é normalizado
para exatamente oito dígitos antes de qualquer chamada aos microsserviços.

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

Quando uma página protegida é acessada sem uma sessão válida, o handler de
autenticação redireciona o navegador para
`/users/login?code=USER_LOGIN_REQUIRED`, onde a orientação para realizar o
login é apresentada. Essa situação não é tratada como erro interno HTTP 500.

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
| `checkout_client.js` | Máscaras, validação e modais do formulário de pagamento. |
| `user_auth.js` | Máscara no cadastro e comportamento dos fluxos de autenticação. |
| `user_profile.js` | Máscara e atualização do WhatsApp. |
| `user_address.js` | Seleção e exclusão dos endereços do perfil. |

Durante operações que aguardam resposta do backend, a tela recebe uma camada
visual de processamento e fica temporariamente indisponível para novas ações.
Submissões canceladas por validação não ativam esse bloqueio.

## Carrinho

O carrinho utiliza a chave `ocipizza.cart` no `localStorage`. Cada item mantém
o identificador, nome, preço, URL da imagem e quantidade da pizza. A quantidade
total é exibida no ícone do menu.

O conteúdo exibido em `GET /cart` é montado no navegador. Ao finalizar o
carrinho, o JavaScript cria campos ocultos contendo somente os identificadores
e as quantidades e submete um formulário tradicional para
`POST /cart/checkout`. Nomes, disponibilidade e preços armazenados no
`localStorage` não são considerados confiáveis pelo backend.

O formulário limita cada item e a soma do pedido a, no máximo, 20 pizzas. O
`CheckoutService` consulta as pizzas e os endereços em paralelo, utiliza os
preços atuais do `pizza-service`, seleciona o endereço principal e consulta o
`delivery-service`. A tela apresenta os itens, a disponibilidade, o subtotal,
a taxa de entrega, o prazo estimado e o total.

O checkout somente pode prosseguir quando todas as pizzas estão disponíveis,
existe um endereço principal e o CEP é elegível para entrega. Sem endereço ou
quando a entrega não estiver disponível, um modal orienta o usuário a acessar
o perfil. Os campos de pagamento permanecem bloqueados nessas situações.

### Pagamento e confirmação do checkout

O formulário de pagamento oferece máscaras e validações no navegador:

- O nome impresso aceita letras e espaços e é convertido para maiúsculas
- O número do cartão aceita 16 dígitos separados em grupos de quatro
- A validade utiliza o formato `MM/AA`
- O código de segurança aceita exatamente três dígitos

Uma tentativa de envio com dados ausentes ou inválidos abre um modal e
posiciona o foco no primeiro campo que precisa ser corrigido. Os dados brutos
do cartão não possuem `name` e, portanto, não são submetidos ao BFF. A futura
integração com o SDK do gateway deverá gerar no navegador um token opaco de
pagamento, enviado no campo `payment_token`.

Ao apresentar o checkout, o BFF gera uma chave UUID de idempotência. Na
confirmação, `POST /cart/checkout/confirm` consulta novamente os serviços e
compara endereço, itens, quantidades, preços, subtotal, taxa e total com os
valores anteriormente apresentados. Qualquer diferença interrompe o fluxo e
redireciona o usuário ao carrinho para revisar os dados atuais.

O token presente no template ainda é fictício e serve apenas ao fluxo de
desenvolvimento; o processamento efetivo pelo gateway de pagamento não faz
parte desta implementação. Após uma revalidação bem-sucedida, o
`CheckoutService` consulta o perfil atual, monta os snapshots do cliente,
endereço e itens e envia o pedido ao `order-service`. Em caso de sucesso, o
usuário é redirecionado ao cardápio, recebe a confirmação visual e o carrinho
armazenado no `localStorage` é esvaziado.

## Mensagens e erros

Os códigos funcionais retornados ou adicionados aos redirects são convertidos
em mensagens em português pelos módulos de `app/messages`. O componente
`templates/components/message.html` mantém a apresentação consistente entre
login, cadastro, cardápio, perfil e endereços.

O serviço possui páginas HTML para os erros `404`, `500`, `502` e `503`. O
handler global renderiza `404.html` para rotas inexistentes e `500.html` para
falhas inesperadas. Respostas HTTP inválidas de qualquer microsserviço exibem
`502.html`, enquanto falhas de conexão exibem `503.html`. Uma resposta `401`
recebida de uma API redireciona para o login, e tentativas de acessar uma rota
com um método HTTP não permitido redirecionam para `/` em vez de apresentar
uma resposta JSON ao usuário.

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
