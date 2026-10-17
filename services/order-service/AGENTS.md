# OCI Pizza - Instruções do order-service

Estas instruções complementam `services/AGENTS.md` e se aplicam somente ao
`order-service`. Em caso de conflito, estas regras específicas têm prioridade.

## Responsabilidade

O `order-service` registra, consulta e atualiza pedidos. Ele preserva snapshots
do cliente, endereço, itens e valores no momento da compra, sem depender de
alterações posteriores no catálogo ou no cadastro do usuário.

O serviço não deve acessar diretamente bancos de dados de outros serviços.
Dados de pizzas, usuários, endereços e entrega devem chegar como parte do
contrato do caso de uso que cria o pedido.

## Organização do código

- `routes/`: recebe requisições, valida autenticação e schemas e monta respostas
  JSend.
- `services/`: concentra regras do ciclo de vida do pedido e orquestra a
  persistência e as notificações.
- `repositories/`: encapsula a persistência dos pedidos.
- `messaging/`: abstrações e publicadores RabbitMQ/OCI Queue.
- `schemas/`: contratos de entrada e saída da API.
- `models/`: modelos internos, estados do pedido e snapshots.
- `dependencies/`: autenticação, persistência e mensageria.

As rotas não devem conter regras de negócio nem acessar repositórios ou
publicadores diretamente.

## Persistência

- O Oracle NoSQL é o provider atualmente implementado e padrão do serviço.
- O acesso deve ocorrer pelo repositório e pela unidade de trabalho fornecidos
  por injeção de dependências.
- O `bootstrap.sh` recria a tabela local de pedidos e pode remover dados
  existentes; não o execute contra dados que precisem ser preservados.
- Não adicione um provider alternativo sem implementar todos os componentes
  necessários e atualizar o `README.md`.
- Valores monetários devem ser tratados com `Decimal` internamente e
  serializados explicitamente antes de compor respostas ou mensagens.

## Autenticação e autorização

- Operações do próprio usuário exigem um access token JWT válido e utilizam o
  `sub` para identificar o proprietário do pedido.
- Operações administrativas exigem `is_admin=true`.
- Operações destinadas à cozinha exigem `is_kitchen=true`.
- Operações permitidas a ambos devem utilizar a dependência compartilhada
  existente, sem duplicar a validação de JWT nas rotas.
- O serviço valida as chaves públicas publicadas pelo `user-service`; não
  consulta o banco de usuários.

## Ciclo de vida do pedido

Os estados válidos são `RECEIVED`, `PREPARING`, `READY`,
`OUT_FOR_DELIVERY`, `DELIVERED` e `CANCELLED`. Alterações de status devem
respeitar as regras do serviço e atualizar o timestamp correspondente.

Pedidos administrativos podem ser consultados, atualizados e excluídos
conforme os endpoints existentes. A exclusão não deve ser adicionada a fluxos
do usuário comum sem uma regra de autorização explícita.

## Mensageria e notificações

- O provider é selecionado por `MESSAGING_PROVIDER`.
- RabbitMQ utiliza `QUEUE_NAME` e deve declarar/publicar na fila configurada.
- OCI Queue utiliza `OCI_QUEUE_ID`, `OCI_QUEUE_MESSAGES_ENDPOINT` e
  `OCI_REGION`, com autenticação por Instance Principal.
- O `OrderEmailService` é responsável por publicar mensagens de notificação;
  o `order-service` não envia e-mails diretamente.
- Os tipos de notificação de pedidos devem permanecer compatíveis com o
  `notification-service`: `ORDER_RECEIVED`, `ORDER_UPDATED`, `ORDER_SENT` e
  `ORDER_DELIVERED`.
- Mensagens devem conter snapshots e valores já serializados, sem depender de
  nova consulta ao pedido pelo consumidor.
- Falhas de publicação devem ser tratadas pelo serviço e não devem expor
  credenciais, tokens ou detalhes internos na resposta HTTP.

## Contratos e qualidade

- Preserve o padrão JSend e os códigos HTTP definidos nas rotas.
- Alterações em endpoints, payloads, estados, filtros, mensagens ou regras de
  autorização devem ser refletidas no `README.md`.
- Não adicione regras de negócio nos schemas, templates ou clientes de
  mensageria.
- Não crie diretórios ou arquivos de testes sem solicitação explícita.
- Preserve alterações existentes e execute apenas as validações pertinentes à
  alteração realizada.
