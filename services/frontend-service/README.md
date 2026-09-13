# OCI Pizza - Frontend Service

## 1. Visão Geral

O `frontend-service` é o serviço responsável pela interface web da aplicação OCI Pizza.

Ele deve consumir APIs dos demais serviços e renderizar o conteúdo por meio de páginas HTML.

O `frontend-service` não expõe API pública própria e não é proprietário de dados de domínio.

## 2. Responsabilidades

O `frontend-service` permite:

- Exibir páginas HTML da aplicação OCI Pizza
- Consumir APIs REST dos serviços de domínio
- Renderizar dados recebidos dos serviços proprietários
- Apoiar fluxos de navegação do usuário
- Tratar estados de carregamento, erro e indisponibilidade de serviços externos

O serviço NÃO é responsável por:

- Implementar regras de negócio dos domínios da aplicação
- Acessar diretamente bancos de dados de outros serviços
- Persistir dados de domínio
- Processar pagamentos
- Gerenciar catálogo de pizzas
- Gerenciar usuários, identidade ou autenticação
- Enviar notificações
- Expor contrato OpenAPI próprio por padrão

## 3. Arquitetura

O serviço atua como camada de apresentação.

As páginas HTML devem ser renderizadas pelo próprio `frontend-service`, usando dados obtidos por chamadas HTTP para os serviços proprietários de cada domínio.

Toda integração deve usar APIs documentadas pelos serviços proprietários. O frontend não deve depender de detalhes internos de implementação, modelos internos, bancos de dados ou arquivos de outros serviços.

Imagens armazenadas no Object Storage devem ser referenciadas por URL pública direta. O frontend apenas monta a URL e a renderiza no HTML para o cliente.

## 4. Integrações

Integrações previstas:

| Serviço                | Uso pelo frontend                                               |
|------------------------|-----------------------------------------------------------------|
| `pizza-service`        | Consulta do catálogo e detalhes de pizzas                       |
| `order-service`        | Criação e acompanhamento de pedidos, quando disponível          |
| `payment-service`      | Fluxos e estados de pagamento, quando disponível                |
| `auth-service`         | Autenticação e sessão do usuário, quando disponível             |
| `user-service`         | Dados de perfil do usuário, quando disponível                   |
| `notification-service` | Preferências e histórico de notificações, quando disponível     |
| `chatbot-service`      | Interações conversacionais e recursos de IA, quando disponível  |

Falhas de comunicação, respostas inesperadas e indisponibilidade temporária dos serviços devem ser tratadas sem quebrar a renderização das páginas.

## 5. Páginas Previstas

| Página      | Objetivo                       |
|-------------|--------------------------------|
| `/`         | Página inicial da aplicação    |
| `/pizzas`   | Listagem do catálogo de pizzas |
| `/cart`     | Visualização do carrinho       |
| `/checkout` | Fluxo de fechamento do pedido  |

Novas páginas devem ser registradas na SPEC quando representarem fluxo relevante da aplicação.

## 6. Estrutura Esperada

```text
frontend-service/
├── app/
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── templates.py
│   │   ├── home_routes.py
│   │   ├── pizza_routes.py
│   │   ├── cart_routes.py
│   │   └── checkout_routes.py
│   ├── clients/
│   │   ├── __init__.py
│   │   └── pizza_service.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── pizzas.html
│   │   ├── cart.html
│   │   └── checkout.html
│   └── static/
│       ├── css/
│       │   └── app.css
│       └── js/
│           └── app.js
├── docs/
│   └── specs/
│       └── frontend-service-spec.md
├── tests/
│   └── test_routes.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .env.example
├── AGENTS.md
└── README.md
```

- `app/main.py`
    - Ponto de entrada da aplicação web.
    - Deve registrar routers e arquivos estáticos.

- `app/routes/`
    - Deve concentrar as rotas de páginas HTML.
    - Deve possuir um módulo por área ou serviço consumido, como `pizza_routes.py`, `cart_routes.py` e `checkout_routes.py`.
    - Rotas devem coordenar renderização e chamadas aos clients, sem implementar regras de negócio de domínio.

- `app/config/settings.py`
    - Deve centralizar a leitura das configurações do serviço.

- `app/clients/`
    - Deve concentrar clientes HTTP para consumo das APIs dos demais serviços.
    - Deve possuir um módulo por serviço consumido, como `pizza_service.py`, `user_service.py` e `order_service.py`.
    - Cada client deve tratar timeouts, falhas de comunicação e respostas inesperadas.

- `app/templates/`
    - Deve conter templates HTML renderizados pelo serviço.

- `app/static/`
    - Deve conter arquivos estáticos da interface, como CSS e JavaScript.

- `tests/`
    - Deve conter testes automatizados das rotas de páginas e comportamentos esperados.

## 7. Configuração

As URLs dos serviços consumidos devem ser configuradas por variáveis de ambiente.

| Variável                   | Descrição                          |
|----------------------------|------------------------------------|
| `PIZZA_SERVICE_URL`        | URL base do `pizza-service`        |
| `PIZZA_IMAGE_BASE_URL`     | URL pública base das imagens de pizzas no Object Storage |
| `ORDER_SERVICE_URL`        | URL base do `order-service`        |
| `PAYMENT_SERVICE_URL`      | URL base do `payment-service`      |
| `AUTH_SERVICE_URL`         | URL base do `auth-service`         |
| `USER_SERVICE_URL`         | URL base do `user-service`         |
| `NOTIFICATION_SERVICE_URL` | URL base do `notification-service` |
| `CHATBOT_SERVICE_URL`      | URL base do `chatbot-service`      |

Valores sensíveis não devem ser versionados. O arquivo `.env.example` deve conter apenas valores locais ou fictícios.

## 8. Regras de Interface

- A interface deve ser simples, responsiva e orientada aos fluxos principais do usuário
- Mensagens exibidas ao usuário devem ser claras e não expor detalhes internos dos serviços
- A ausência ou indisponibilidade de dados externos deve ser tratada de forma controlada
- O frontend não deve duplicar validações de domínio como fonte de verdade
- Validações críticas pertencem aos serviços responsáveis pelos domínios

## 9. Desenvolvimento Local

O ambiente local deve usar as automações do projeto.

Comandos principais a partir da raiz do repositório:

```bash
make development-up
make build
```

O `frontend-service` é iniciado pelo `docker-compose.yaml` e fica disponível localmente em:

```text
http://localhost:8085
```

Para executar somente o serviço de frontend com suas dependências declaradas no Compose:

```bash
docker compose up frontend-service
```

Quando houver automação específica de testes para o `frontend-service` no `Makefile`, este README deve ser atualizado.

## 10. Documentação

A fonte funcional e arquitetural do serviço é `docs/specs/frontend-service-spec.md`.

O `frontend-service` não deve possuir `docs/api/openapi.yaml` por padrão, pois não expõe API própria.

Sempre que responsabilidades, estrutura, execução, configuração, páginas, integrações ou comportamento documentado forem alterados, a SPEC e este README devem ser revisados.
