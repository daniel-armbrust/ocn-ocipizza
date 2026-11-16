#
# logging/locals.tf
#

locals {
  # Nome único do grupo regional que concentra os logs da aplicação.
  log_group_name = "loggroup-ocipizza"

  # Cada serviço possui um log próprio para facilitar a consulta e a retenção.
  log_names = toset([
    "log-pizza-service",
    "log-admin-service",
    "log-chatbot-service",
    "log-delivery-service",
    "log-frontend-service",
    "log-notification-service",
    "log-order-service",
    "log-user-service",
  ])

  # Retenção inicial didática de 30 dias, em conformidade com o OCI Logging.
  retention_duration = 30
}
