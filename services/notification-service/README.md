# OCI Pizza — Notification Service

## Responsabilidade do serviço

O `notification-service` executa um worker que consome mensagens de uma fila,
renderiza templates Jinja2 e envia notificações por e-mail. A aplicação FastAPI
mantém o worker ativo durante seu ciclo de vida e expõe somente o health check e
a documentação interativa em desenvolvimento.

O fluxo de processamento é:

1. O consumidor recebe uma mensagem do provider configurado.
2. O worker entrega o corpo da mensagem ao `NotificationService`.
3. O serviço seleciona e renderiza o template correspondente.
4. O provider de e-mail envia o conteúdo renderizado.
5. A mensagem é confirmada ou excluída somente depois do envio bem-sucedido.

Quando o processamento falha, a mensagem não é confirmada e pode voltar a
ficar disponível de acordo com a política do provider de mensageria. Mensagens
que não contêm JSON válido são descartadas para evitar novas tentativas.

## Dependências

| Componente | Responsabilidade |
| --- | --- |
| RabbitMQ | Provider local de consumo das mensagens de notificação. |
| OCI Queue | Provider OCI alternativo de mensageria. |
| Mailpit/SMTP | Envio e inspeção de e-mails no ambiente local. |
| OCI Email Delivery | Provider OCI alternativo para envio de e-mails. |

As dependências Python são instaladas por `requirements.txt`:

| Biblioteca | Versão | Uso principal |
| --- | --- | --- |
| FastAPI | 0.141.1 | Ciclo de vida do worker, health check e servidor ASGI. |
| pydantic-settings | 2.10.1 | Leitura das configurações de ambiente. |
| Jinja2 | 3.1.6 | Renderização dos templates HTML. |
| pika | 1.3.2 | Consumo e confirmação de mensagens no RabbitMQ. |
| OCI SDK | 2.160.3 | Integração com OCI Queue, Email Delivery e Logging. |

O ambiente de execução utiliza Python 3.11.

## Contrato das mensagens

Cada mensagem deve conter um objeto JSON com, no mínimo:

```json
{
  "type": "USER_CONFIRMATION",
  "recipient": "ana.laura@example.com",
  "full_name": "Ana Laura",
  "token": "TOKEN_DE_CONFIRMACAO"
}
```

Os campos `type` e `recipient` controlam o processamento. Os demais campos são
encaminhados ao preparador e ao template do tipo selecionado.

### Tipos implementados

| Tipo | Estado | Dados específicos |
| --- | --- | --- |
| `USER_CONFIRMATION` | Implementado | `full_name` e `token`. |

Para `USER_CONFIRMATION`, o link enviado por e-mail é construído como
`{SITE_URL}/users/confirm?token=...`.

<!-- TODO: Implementar e alinhar os identificadores, preparadores e templates
de redefinição de senha e de pedido enviado. Atualmente USER_PASSWORD_RESET,
USER_ORDER_SENT e ORDER_SENT não formam fluxos completos e não devem ser
publicados em produção. -->

## Mensageria

O provider é selecionado por `MESSAGING_PROVIDER`.

### RabbitMQ

Use `MESSAGING_PROVIDER=rabbitmq` e configure `QUEUE_NAME`, `RABBITMQ_HOST`,
`RABBITMQ_PORT`, `RABBITMQ_USERNAME` e `RABBITMQ_PASSWORD`.

O consumidor declara a fila como durável, utiliza `prefetch_count=1`, recebe
uma mensagem por vez com `basic_get` e executa `basic_ack` somente depois do
envio do e-mail.

### OCI Queue

Use `MESSAGING_PROVIDER=oci_queue` e configure `OCI_QUEUE_ID`,
`OCI_QUEUE_MESSAGES_ENDPOINT` e `OCI_REGION`.

`OCI_QUEUE_MESSAGES_ENDPOINT` deve conter o `messagesEndpoint` específico da
fila, e não o endpoint administrativo do serviço. O consumidor solicita no
máximo uma mensagem e a exclui usando o `receipt` somente depois do
processamento bem-sucedido.

O provider OCI autentica por Instance Principal. A instância deve pertencer a
um Dynamic Group autorizado por uma IAM Policy a consumir e excluir mensagens.
A aplicação não utiliza arquivo de configuração OCI nem API key.

## Providers de e-mail

O provider é selecionado por `EMAIL_PROVIDER`.

### SMTP

Use `EMAIL_PROVIDER=smtp` e configure host, porta e remetente. Usuário e senha
são opcionais; a autenticação ocorre somente quando ambos estão preenchidos.
`SMTP_USE_TLS=true` habilita STARTTLS. Em desenvolvimento, o projeto utiliza o
Mailpit sem autenticação e sem TLS.

### OCI Email Delivery

Use `EMAIL_PROVIDER=oci`. O cliente usa a API de data plane do OCI Email
Delivery e autentica por Instance Principal. O remetente precisa estar aprovado
e a instância precisa das permissões IAM correspondentes.

<!-- TODO: Alinhar a assinatura de OciEmailSender.send com EmailSender antes de
utilizar EMAIL_PROVIDER=oci. Atualmente EmailService encaminha body_text, mas a
implementação OCI não aceita esse argumento. -->

## Configurações

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `APP_NAME` | `notification-service` | Nome da aplicação. |
| `APP_ENV` | `development` | Ambiente de execução. |
| `DEBUG` | `false` | Ativa o modo de depuração. |
| `SITE_URL` | `https://www.ocipizza.com.br` | URL pública usada nos links dos e-mails. |
| `MESSAGING_PROVIDER` | Obrigatório | `rabbitmq` ou `oci_queue`. |
| `QUEUE_NAME` | `notifications-queue` | Nome lógico da fila. |
| `NOTIFICATION_POLL_INTERVAL` | `5.0` | Espera quando nenhuma mensagem está disponível. |
| `NOTIFICATION_RETRY_INTERVAL` | `10.0` | Espera depois de uma falha no ciclo de consumo. |
| `RABBITMQ_HOST` | — | Host obrigatório para RabbitMQ. |
| `RABBITMQ_PORT` | — | Porta obrigatória para RabbitMQ. |
| `RABBITMQ_USERNAME` | — | Usuário obrigatório para RabbitMQ. |
| `RABBITMQ_PASSWORD` | — | Senha obrigatória para RabbitMQ. |
| `OCI_QUEUE_ID` | — | OCID obrigatório para OCI Queue. |
| `OCI_QUEUE_MESSAGES_ENDPOINT` | — | Endpoint obrigatório para OCI Queue. |
| `OCI_REGION` | `sa-saopaulo-1` | Região dos serviços OCI. |
| `EMAIL_PROVIDER` | `smtp` | `smtp` ou `oci`. |
| `EMAIL_TEMPLATES_PATH` | `app/templates/emails` | Diretório dos templates HTML. |
| `SMTP_HOST` | — | Host utilizado pelo provider SMTP. |
| `SMTP_PORT` | — | Porta utilizada pelo provider SMTP. |
| `SMTP_USERNAME` | — | Usuário SMTP opcional. |
| `SMTP_PASSWORD` | — | Senha SMTP opcional. |
| `SMTP_USE_TLS` | `true` | Habilita STARTTLS no provider SMTP. |
| `SMTP_EMAIL_SENDER` | `no-reply@ocipizza.com.br` | Endereço remetente. |
| `OCI_EMAIL_DELIVERY_COMPARTMENT_ID` | — | Compartment do OCI Email Delivery. |
| `OCI_EMAIL_SENDER_NAME` | `OCI Pizza` | Nome apresentado como remetente. |
| `LOG_LEVEL` | `INFO` | Nível global de logging. |
| `OCI_LOG_ID` | — | OCID do Custom Log usado fora de desenvolvimento. |

<!-- TODO: O docker-compose.yaml ainda define SMTP_FROM_EMAIL, mas o Settings
consome SMTP_EMAIL_SENDER. Alinhar o nome no Compose antes de depender de um
remetente diferente do valor padrão. -->

## Execução local

Com RabbitMQ e Mailpit disponíveis, execute:

```bash
cd services/notification-service
./startdev.sh
```

O script utiliza RabbitMQ em `localhost:5672`, Mailpit em `localhost:1025`, a
fila `notifications-queue` e inicia o FastAPI na porta `8005`.

Pelo Docker Compose, a partir da raiz do monorepo:

```bash
docker compose up -d notification-service
docker compose logs -f notification-service
```

No Docker Compose, a porta do serviço não é publicada no host. O health check
fica acessível apenas pela rede interna na porta `8000`, salvo configuração
adicional.

## API e ciclo de vida

| Método | Rota | Acesso | Comportamento |
| --- | --- | --- | --- |
| `GET` | `/health` | Público | Retorna o estado básico do serviço. |

O worker é iniciado no `lifespan` do FastAPI e cancelado durante o shutdown.
Não existem endpoints HTTP para publicar ou processar notificações; a entrada
ocorre exclusivamente pelo provider de mensageria.

Em `development`, Swagger UI, ReDoc e OpenAPI JSON ficam disponíveis em
`/docs`, `/redoc` e `/openapi.json`. Fora de `development`, essas interfaces são
desabilitadas.

## Logging

Em `development`, os logs são enviados para `stdout`. Fora de `development`, o
serviço também utiliza OCI Logging com Instance Principal e exige `OCI_LOG_ID`.
Falhas de consumo e processamento são registradas sem encerrar definitivamente
o worker.
