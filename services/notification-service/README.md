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
| `USER_PASSWORD_RESET` | Implementado | `full_name` e `token`. |
| `ORDER_RECEIVED` | Implementado | Dados do cliente, pedido, itens e valores. |
| `ORDER_UPDATED` | Implementado | Cliente, pedido, novo status e data da atualização. |
| `ORDER_SENT` | Implementado | Pedido enviado para entrega, status e data da atualização. |
| `ORDER_DELIVERED` | Implementado | Pedido entregue, status e data da atualização. |

### Preparação dos templates

O `EmailTemplateService` coordena a renderização e delega a preparação dos
dados para serviços separados por domínio:

- `UserEmailTemplateService`: confirmações de conta e redefinição de senha.
- `OrderEmailTemplateService`: pedido recebido e notificações de atualização,
  envio e entrega.

Essa separação mantém as validações específicas de usuários e pedidos fora do
renderizador central. Antes de carregar o template Jinja2, os preparadores
validam os campos obrigatórios e complementam os dados necessários, como o
rótulo amigável do status do pedido.

Para `USER_CONFIRMATION`, o link enviado por e-mail é construído como
`{SITE_URL}/users/confirm?token=...`.

Para `USER_PASSWORD_RESET`, o link enviado por e-mail é construído como
`{SITE_URL}/users/password-reset/confirm?token=...`. O preparador exige
`full_name` e `token`; mensagens sem esses campos não são processadas.

Para `ORDER_RECEIVED`, o e-mail informa que o pedido foi recebido, apresenta
os itens e o resumo financeiro e avisa que o cliente será notificado quando as
pizzas saírem para entrega.

O contrato esperado para esse tipo é:

```json
{
  "type": "ORDER_RECEIVED",
  "recipient": "ana.laura@example.com",
  "full_name": "Ana Laura",
  "order_id": "93da1548-90ba-4b69-83e2-dfe4d42bcdb4",
  "items": [
    {
      "name": "Margherita",
      "quantity": 2,
      "unit_price": "45.00",
      "total": "90.00"
    }
  ],
  "subtotal": "90.00",
  "delivery_fee": "10.00",
  "total": "100.00"
}
```

`items` deve ser uma lista não vazia. Cada item deve conter `name`, `quantity`,
`unit_price` e `total`. Os campos monetários `unit_price`, `items[].total`,
`subtotal`, `delivery_fee` e `total` são recebidos como strings decimais com
exatamente duas casas e renderizados no e-mail com o prefixo `R$`.

Para `ORDER_UPDATED`, o e-mail informa o novo status do pedido ao cliente. O
contrato esperado é:

```json
{
  "type": "ORDER_UPDATED",
  "recipient": "ana.laura@example.com",
  "full_name": "Ana Laura",
  "order_id": "93da1548-90ba-4b69-83e2-dfe4d42bcdb4",
  "status": "PREPARING",
  "updated_at": "2026-10-15T13:28:56.806000+00:00"
}
```

Para as notificações específicas de saída e entrega, o contrato mantém os
mesmos campos de `ORDER_UPDATED`, mas exige os respectivos status:

- `ORDER_SENT` exige `status="OUT_FOR_DELIVERY"`.
- `ORDER_DELIVERED` exige `status="DELIVERED"`.

O `OrderEmailTemplateService` rejeita mensagens que utilizem um status
incompatível com o tipo da notificação antes de renderizar o template.

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

### Propósito do `startdev.sh`

O script `startdev.sh` automatiza a execução local do
`notification-service`. Ele configura o RabbitMQ como provider de mensageria,
seleciona SMTP com Mailpit como provider de e-mail, define a fila
`notifications-queue`, cria e ativa o ambiente virtual `.venv` quando
necessário, instala as dependências de `requirements.txt` e inicia o Uvicorn
com recarregamento automático na porta `8005`.

Ao iniciar o FastAPI, o ciclo de vida da aplicação também inicia o worker que
consome as mensagens da fila. Portanto, o script não apenas inicia o endpoint
de health check: ele coloca o consumidor de notificações em execução.

O script é exclusivo para desenvolvimento local. As configurações de RabbitMQ
e Mailpit são valores locais e não devem ser utilizadas em produção; nesse
ambiente, selecione os providers e forneça as credenciais por configuração
segura.

O `startdev.sh` configura diretamente RabbitMQ e SMTP com Mailpit. Para manter
uma configuração local própria ou selecionar outros providers, copie o arquivo
de exemplo e inicie o Uvicorn sem o script:

```bash
cp .env.example .env
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
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

## Estrutura principal

| Diretório | Responsabilidade |
| --- | --- |
| `app/messaging/` | Consumidores RabbitMQ e OCI Queue. |
| `app/workers/` | Ciclo de consumo e processamento das mensagens. |
| `app/services/` | Renderização dos templates e envio das notificações. |
| `app/templates/emails/` | Templates HTML dos e-mails de usuários e pedidos. |
| `app/clients/` | Implementações SMTP e OCI Email Delivery. |

## Logging

Em `development`, os logs são enviados para `stdout`. Fora de `development`, o
serviço também utiliza OCI Logging com Instance Principal e exige `OCI_LOG_ID`.
Falhas de consumo e processamento são registradas sem encerrar definitivamente
o worker.
