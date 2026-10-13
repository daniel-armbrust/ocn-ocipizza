# Notification Service

Serviço responsável por consumir solicitações de notificação e enviá-las pelo
canal configurado.

## Mensageria

O provider é selecionado por `MESSAGING_PROVIDER`:

- `rabbitmq`: utiliza `QUEUE_NAME`, `RABBITMQ_HOST`, `RABBITMQ_PORT`,
  `RABBITMQ_USERNAME` e `RABBITMQ_PASSWORD`.
- `oci_queue`: utiliza `OCI_QUEUE_ID`, `OCI_QUEUE_MESSAGES_ENDPOINT` e
  `OCI_REGION`.

O provider OCI Queue autentica por Instance Principal. A instância deve
pertencer a um Dynamic Group autorizado por uma IAM Policy a consumir e
excluir mensagens da fila. Nenhum arquivo de configuração OCI ou API key é
utilizado pela aplicação.

`OCI_QUEUE_MESSAGES_ENDPOINT` deve conter o `messagesEndpoint` específico da
fila, e não o endpoint administrativo do serviço OCI Queue.
