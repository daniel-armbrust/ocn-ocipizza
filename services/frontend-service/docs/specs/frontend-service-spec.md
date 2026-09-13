# Frontend Service Specification

## 1. Objetivo

O `frontend-service` é responsável pela interface web da aplicação OCI Pizza.

O serviço deve consumir APIs dos demais serviços da aplicação e renderizar o conteúdo por meio de páginas HTML.

## 2. Escopo

O `frontend-service` deve permitir:

- Exibir páginas HTML da aplicação OCI Pizza
- Consultar dados dos serviços de domínio por meio de suas APIs REST
- Renderizar o catálogo de pizzas com dados fornecidos pelo `pizza-service`
- Renderizar dados de autenticação e perfil com dados fornecidos por `auth-service` e `user-service`, quando disponíveis
- Renderizar dados de pedidos com dados fornecidos pelo `order-service`, quando disponível
- Renderizar etapas e estados de pagamento com dados fornecidos pelo `payment-service`, quando disponível
- Renderizar mensagens e preferências de notificação com dados fornecidos pelo `notification-service`, quando disponível
- Renderizar interações conversacionais com dados fornecidos pelo `chatbot-service`, quando disponível
- Apoiar fluxos de navegação do usuário na interface web
- Apresentar estados de carregamento, erro e indisponibilidade de serviços externos

O `frontend-service` NÃO é responsável por:

- Expor API pública própria
- Implementar regras de negócio dos domínios da aplicação
- Acessar diretamente bancos de dados de outros serviços
- Persistir dados de domínio
- Processar pagamentos
- Gerenciar catálogo de pizzas
- Gerenciar usuários, identidade ou autenticação
- Enviar notificações

## 3. Arquitetura

O serviço atua como camada de apresentação.

As páginas HTML devem ser renderizadas pelo próprio `frontend-service`, utilizando dados obtidos por chamadas HTTP para os serviços proprietários de cada domínio.

Toda integração com outro serviço deve ocorrer por meio de APIs documentadas pelo serviço proprietário. O `frontend-service` não deve depender de detalhes internos de implementação, banco de dados, modelos internos ou arquivos de outros serviços.

Os clients HTTP devem ficar em `app/clients/`, organizados em um módulo por serviço consumido. Exemplos: `pizza_service.py`, `user_service.py`, `order_service.py`, `payment_service.py`, `notification_service.py` e `chatbot_service.py`.

Imagens armazenadas no Object Storage devem ser referenciadas por URL pública direta. O `frontend-service` deve apenas montar e renderizar a URL para o cliente, sem fazer proxy ou streaming dos arquivos.

Como o `frontend-service` não expõe API própria, ele não deve possuir `docs/api/openapi.yaml` por padrão. Esse contrato só deve ser criado se o serviço passar a expor endpoints próprios com contrato técnico relevante.

## 4. Integrações

Integrações esperadas:

| Serviço                | Responsabilidade Consumida                                     |
|------------------------|----------------------------------------------------------------|
| `pizza-service`        | Consulta do catálogo e detalhes de pizzas                      |
| `order-service`        | Criação e acompanhamento de pedidos, quando disponível         |
| `payment-service`      | Fluxos de pagamento, quando disponível                         |
| `auth-service`         | Autenticação e sessão do usuário, quando disponível            |
| `user-service`         | Dados de perfil do usuário, quando disponível                  |
| `notification-service` | Preferências e histórico de notificações, quando disponível    |
| `chatbot-service`      | Interações conversacionais e recursos de IA, quando disponível |

As integrações devem tratar falhas de comunicação, respostas inesperadas e indisponibilidade temporária dos serviços.

## 5. Páginas

Páginas previstas:

| Página      | Objetivo                       |
|-------------|--------------------------------|
| `/`         | Página inicial da aplicação    |
| `/pizzas`   | Listagem do catálogo de pizzas |
| `/cart`     | Visualização do carrinho       |
| `/checkout` | Fluxo de fechamento do pedido  |

Novas páginas devem ser registradas nesta SPEC quando representarem fluxo relevante da aplicação.

## 6. Configuração

As URLs dos serviços consumidos devem ser configuradas por variáveis de ambiente.

Variáveis previstas:

| Variável                   | Descrição                            |
|----------------------------|--------------------------------------|
| `PIZZA_SERVICE_URL`        | URL base do `pizza-service`          |
| `PIZZA_IMAGE_BASE_URL`     | URL pública base das imagens de pizzas no Object Storage |
| `ORDER_SERVICE_URL`        | URL base do `order-service`          |
| `PAYMENT_SERVICE_URL`      | URL base do `payment-service`        |
| `AUTH_SERVICE_URL`         | URL base do `auth-service`           |
| `USER_SERVICE_URL`         | URL base do `user-service`           |
| `NOTIFICATION_SERVICE_URL` | URL base do `notification-service`   |
| `CHATBOT_SERVICE_URL`      | URL base do `chatbot-service`        |

Valores sensíveis não devem ser versionados. Arquivos de exemplo devem usar apenas valores locais ou fictícios.

## 7. Regras de Interface

- A interface deve ser simples, responsiva e orientada aos fluxos principais do usuário
- Mensagens exibidas ao usuário devem ser claras e não expor detalhes internos dos serviços
- A ausência ou indisponibilidade de dados externos deve ser tratada de forma controlada
- O frontend não deve duplicar validações de domínio como fonte de verdade; validações críticas pertencem aos serviços responsáveis

## 8. Critérios de Aceite

- O serviço renderiza páginas HTML sem expor API pública própria
- Dados de domínio são obtidos por meio das APIs dos serviços proprietários
- Dados de pedidos, pagamentos, autenticação, usuários, notificações e chatbot são obtidos por meio das APIs dos respectivos serviços quando esses fluxos forem exibidos
- Falhas em serviços externos são tratadas sem quebrar a renderização da página
- Configurações de URLs externas são fornecidas por variáveis de ambiente
- O `README.md` é revisado e atualizado quando houver mudança em responsabilidades, estrutura, execução, configuração, páginas, integrações ou comportamento documentado
