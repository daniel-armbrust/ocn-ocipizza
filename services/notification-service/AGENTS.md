# OCI Pizza - Instruções do notification-service

Estas instruções complementam `services/AGENTS.md` e se aplicam somente ao
`notification-service`. Em caso de conflito, estas regras específicas têm prioridade.

## Responsabilidade

O `notification-service` executa o worker responsável por consumir mensagens,
preparar templates e enviar notificações por e-mail. Ele não deve implementar
regras de usuários ou pedidos nem acessar os bancos de dados desses serviços.

O serviço expõe apenas endpoints operacionais da aplicação e mantém o worker
ativo durante o ciclo de vida do processo FastAPI.

## Organização do código

- `messaging/`: abstrações e implementações dos consumidores de RabbitMQ e OCI
  Queue.
- `workers/`: ciclo de consumo, processamento e confirmação das mensagens.
- `services/`: orquestração do envio e preparação dos dados dos e-mails.
- `clients/`: integrações com SMTP/Mailpit e OCI Email Delivery.
- `templates/emails/`: templates HTML dos e-mails.
- `notifications/`: catálogo dos tipos de notificação e seus templates.

O consumidor não deve renderizar templates nem enviar e-mails diretamente. O
worker deve delegar o processamento ao `NotificationService`.

## Mensageria

- O provider é selecionado por `MESSAGING_PROVIDER`.
- RabbitMQ utiliza `QUEUE_NAME`, declara a fila como durável e confirma a
  mensagem somente depois do envio bem-sucedido.
- OCI Queue utiliza `OCI_QUEUE_ID`, `OCI_QUEUE_MESSAGES_ENDPOINT` e
  `OCI_REGION`, autenticando por Instance Principal.
- O `OCI_QUEUE_MESSAGES_ENDPOINT` deve ser o `messagesEndpoint` específico da
  fila, não o endpoint administrativo do OCI Queue.
- Mensagens inválidas ou que não contenham JSON válido devem ser descartadas
  conforme o comportamento documentado do consumidor.
- Falhas durante o processamento não devem confirmar a mensagem; ela deve
  permanecer disponível de acordo com a política do provider.
- Não altere a estrutura dos payloads sem atualizar os produtores e o
  `README.md`.

## Contrato das notificações

Toda mensagem deve conter `type` e `recipient`. Os tipos atualmente suportados
são:

- `USER_CONFIRMATION`
- `USER_PASSWORD_RESET`
- `ORDER_RECEIVED`
- `ORDER_UPDATED`
- `ORDER_SENT`
- `ORDER_DELIVERED`

Os dados específicos de usuários e pedidos devem ser preparados por serviços
separados, como `UserEmailTemplateService` e `OrderEmailTemplateService`.
Validações de campos obrigatórios e compatibilidade de status devem ocorrer
antes da renderização do template.

Tokens recebidos nas mensagens podem ser usados somente para construir links de
confirmação ou redefinição. Nunca devem ser persistidos, registrados em logs
ou incluídos em mensagens de erro.

## E-mails e templates

- `EMAIL_PROVIDER=smtp` deve ser utilizado no desenvolvimento com Mailpit.
- `EMAIL_PROVIDER=oci` utiliza OCI Email Delivery e Instance Principal.
- O remetente e as credenciais devem vir da configuração, nunca do código.
- Templates devem permanecer em `app/templates/emails/` e seguir o padrão
  visual existente.
- Templates HTML não devem conter regras de negócio nem acesso a serviços.
- Novos tipos de notificação devem ser registrados no catálogo de templates,
  no preparador de dados, no serviço de renderização e no `README.md`.
- Alterações em payloads, assuntos ou links devem ser avaliadas também no
  serviço produtor da mensagem.

## Operação e qualidade

- O worker deve confirmar ou excluir mensagens somente após o envio bem-sucedido.
- Falhas devem ser registradas sem expor tokens, senhas ou dados sensíveis.
- Atualize `README.md` quando forem alterados providers, mensagens, templates,
  variáveis de ambiente ou comportamento do worker.
- Não crie diretórios ou arquivos de testes sem solicitação explícita.
- Preserve alterações existentes e execute apenas as validações pertinentes à
  alteração realizada.
