# OCI Pizza — Admin Service

## Responsabilidade do serviço

O `admin-service` é o painel web administrativo da OCI Pizza. Ele funciona
como um BFF (Backend For Frontend): renderiza as páginas HTML, valida os
formulários recebidos do navegador e chama os microsserviços responsáveis
pelos dados.

O serviço possui duas áreas de acesso:

- **Administração**: gerenciamento de pedidos, pizzas e demais recursos
  administrativos.
- **Cozinha**: acompanhamento dos pedidos e atualização dos estados de preparo.

O navegador não recebe tokens JWT. Após o login, o serviço mantém os tokens em
uma sessão persistida no Redis e envia ao navegador somente o identificador
opaco da sessão em um cookie `HttpOnly`.

## Dependências

| Componente | Responsabilidade |
| --- | --- |
| `user-service` | Autenticação, autorização, revogação de sessões e JWKS. |
| `order-service` | Consulta, atualização e exclusão de pedidos. |
| `pizza-service` | Consulta e gerenciamento do catálogo de pizzas. |
| `delivery-service` | Consulta e gerenciamento das áreas, taxas e prazos de entrega. |
| `notification-service` | Serviço disponível para futuras funcionalidades administrativas de notificação. |
| Redis | Persistência das sessões opacas do painel. |

O `admin-service` não acessa diretamente os bancos de dados dos outros
serviços.

## Autenticação e autorização

O login é realizado em `POST /admin/login`. O perfil retornado pelo
`user-service` define o destino:

- usuários com `is_admin=true` seguem para `/admin/dashboard`;
- usuários com `is_kitchen=true` seguem para `/kitchen/orders`.

As rotas administrativas utilizam `get_admin_authenticated_session` e as
rotas da cozinha utilizam `get_kitchen_authenticated_session`. Usuários sem
sessão válida são redirecionados para `/admin/login`.

O logout é exposto por `POST /admin/logout` e `POST /kitchen/logout`. O serviço
tenta revogar o refresh token no `user-service` e remove a sessão local mesmo
quando o serviço remoto não está disponível.

## Rotas web

### Autenticação

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/admin/login` | Público | Exibe o formulário de login. |
| `POST` | `/admin/login` | Público | Valida o formulário, autentica e cria a sessão. |
| `POST` | `/admin/logout` | Autenticado | Encerra uma sessão administrativa. |
| `POST` | `/kitchen/logout` | Autenticado | Encerra uma sessão da cozinha. |

### Administração de pedidos

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/admin/dashboard` | Admin | Exibe a visão geral do painel. |
| `GET` | `/admin/orders` | Admin | Lista pedidos com filtro e paginação. |
| `GET` | `/admin/orders/{order_id}` | Admin | Exibe os detalhes de um pedido. |
| `POST` | `/admin/orders/{order_id}/status` | Admin | Atualiza o status do pedido. |
| `POST` | `/admin/orders/{order_id}/delete` | Admin | Exclui um pedido após confirmação. |

O formulário administrativo envia o novo status ao BFF. Internamente, o
`admin-service` delega a alteração ao `order-service`, que utiliza o contrato
de atualização de status do domínio de pedidos.

### Administração de pizzas

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/admin/pizzas` | Admin | Lista pizzas com filtro e paginação. |
| `GET` | `/admin/pizzas/new` | Admin | Exibe o formulário de criação. |
| `POST` | `/admin/pizzas` | Admin | Cria uma pizza e envia sua imagem ao `pizza-service`. |
| `GET` | `/admin/pizzas/{pizza_id}` | Admin | Exibe os detalhes e o formulário de edição. |
| `POST` | `/admin/pizzas/{pizza_id}/edit` | Admin | Atualiza dados, disponibilidade e imagem da pizza. |
| `POST` | `/admin/pizzas/{pizza_id}/delete` | Admin | Exclui a pizza após confirmação. |

As operações de criação e edição utilizam `multipart/form-data`. O campo
`image` contém o arquivo da imagem; o `admin-service` não gera nem persiste o
nome do objeto, pois essa responsabilidade pertence ao `pizza-service`.

Os botões de salvar e excluir na página de detalhes exibem um modal de
confirmação antes do envio do formulário.

### Administração das áreas de entrega

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/admin/delivery/areas` | Admin | Lista áreas com filtro de status e paginação. |
| `GET` | `/admin/delivery/areas/new` | Admin | Exibe o formulário de criação. |
| `POST` | `/admin/delivery/areas` | Admin | Cria uma área com faixa de CEP, taxa e prazo. |
| `GET` | `/admin/delivery/areas/{delivery_area_id}` | Admin | Exibe os dados e o formulário de edição. |
| `PUT` | `/admin/delivery/areas/{delivery_area_id}` | Admin | Atualiza os dados da área. |
| `POST` | `/admin/delivery/areas/{delivery_area_id}` | Admin | Atualiza os dados pelo formulário HTML. |

As rotas de escrita validam os dados com `WTForms`, chamam o
`DeliveryService` e sempre retornam `303 See Other`. O serviço delega as
operações ao contrato administrativo do `delivery-service`. O `PUT` mantém o
contrato HTTP explícito, enquanto o `POST` existe para permitir o envio por
formulários HTML, que não suportam `PUT` nativamente. O navegador não recebe
respostas JSON diretamente.

### Operação da cozinha

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/kitchen/orders` | Cozinha | Lista pedidos operacionais com filtro e paginação. |
| `GET` | `/kitchen/orders/{order_id}` | Cozinha | Exibe os detalhes operacionais do pedido. |
| `POST` | `/kitchen/orders/{order_id}/status` | Cozinha | Permite marcar o pedido como em preparo ou pronto. |

As ações **Iniciar preparo** e **Marcar como pronto** exigem confirmação em
modal antes da submissão.

## Formulários e fluxo de redirecionamento

As submissões HTML utilizam `WTForms` e `python-multipart`. As rotas validam o
formulário antes de chamar qualquer microsserviço e seguem o padrão
Post/Redirect/Get: tanto sucesso quanto falha terminam em um redirecionamento
`303 See Other`.

Os códigos funcionais enviados na query string são convertidos em mensagens
pelos mapeamentos em `app/messages/` e exibidos pelo modal global de mensagens.
As operações de escrita são protegidas por CSRF.

O JavaScript também bloqueia a tela durante submissões e navegações que podem
gerar uma chamada ao backend, evitando envios duplicados.

## Configuração

As configurações são lidas de variáveis de ambiente. Consulte
[`.env.example`](.env.example) para a lista completa.

| Variável | Descrição |
| --- | --- |
| `APP_ENV` | Ambiente de execução; `development` habilita documentação da API e integrações locais. |
| `PERSISTENCE_PROVIDER` | Provider das sessões; Redis é o padrão. |
| `REDIS_ENDPOINT` | Endpoint do Redis usado para as sessões. |
| `SESSION_SECRET_KEY` | Chave do middleware de sessão. |
| `CSRF_SECRET_KEY` | Chave usada na proteção CSRF. |
| `PIZZA_SERVICE_URL` | URL do `pizza-service`. |
| `USER_SERVICE_URL` | URL do `user-service`. |
| `DELIVERY_SERVICE_URL` | URL do `delivery-service`. |
| `ORDER_SERVICE_URL` | URL do `order-service`. |
| `NOTIFICATION_SERVICE_URL` | URL do `notification-service`. |
| `JWT_ISSUER` | Emissor esperado nos tokens JWT. |
| `JWT_AUDIENCE` | Audiência esperada nos tokens JWT; o padrão é `ocipizza`. |
| `JWT_JWKS_URL` | Endpoint das chaves públicas do `user-service`. |
| `HTTP_CLIENT_TIMEOUT` | Timeout das chamadas aos microsserviços. |

As chaves de sessão, CSRF e credenciais de produção devem ser fornecidas por
um mecanismo seguro de configuração e nunca versionadas no repositório.

## Execução local

O serviço utiliza Python 3.11. Com os demais serviços e o Redis disponíveis,
execute a partir do diretório do serviço:

### Propósito do `startdev.sh`

O script `startdev.sh` automatiza a execução local do `admin-service`. Ele
define as variáveis de ambiente de desenvolvimento, configura as URLs dos
microsserviços, prepara o ambiente virtual `.venv`, instala as dependências de
`requirements.txt` e inicia o Uvicorn com recarregamento automático na porta
`8006`.

O script é destinado exclusivamente ao desenvolvimento local. As chaves de
sessão e CSRF presentes nele são valores de demonstração e não devem ser
utilizadas em produção. Em ambientes OCI ou outros ambientes compartilhados,
forneça essas configurações por um mecanismo seguro e execute o serviço pelo
processo de deployment correspondente.

```bash
cd services/admin-service
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./startdev.sh
```

O servidor de desenvolvimento fica disponível em:

```text
http://localhost:8006
```

Para executar pelo Docker Compose a partir da raiz do repositório:

```bash
docker compose up -d admin-service
docker compose ps admin-service
```

Em ambiente de desenvolvimento, a documentação automática do FastAPI fica
disponível em `/docs` e `/redoc`.

## Estrutura da interface

| Diretório | Responsabilidade |
| --- | --- |
| `app/routes/` | Rotas HTML, autenticação e delegação aos serviços de aplicação. |
| `app/services/` | Serviços de autenticação, sessão, pedidos, pizzas e entregas. |
| `app/clients/` | Clientes HTTP para comunicação com os microsserviços. |
| `app/forms/` | Formulários e validações recebidos do navegador. |
| `app/templates/` | Templates Jinja das áreas administrativa, cozinha, login e erros. |
| `app/static/css/` | Folhas de estilo separadas por área funcional. |
| `app/static/js/` | Módulos JavaScript separados por área funcional. |
| `app/static/img/` | Imagens e elementos gráficos estáticos. |

O arquivo `app/static/css/admin.css` funciona como manifesto dos estilos e
`app/static/js/admin.js` como ponto de entrada dos módulos JavaScript.
O módulo `app/static/js/delivery.js` aplica a máscara de CEP nos formulários
de áreas de entrega.

## Tratamento de erros

Falhas de autenticação, autorização, CSRF e comunicação com os serviços
upstream são tratadas por handlers globais ou pelas rotas, conforme o tipo da
operação. Navegações protegidas retornam ao login; falhas de comunicação
durante páginas HTML são apresentadas pelas páginas de erro do painel.
