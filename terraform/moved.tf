#
# moved.tf
#

# Preserva o Service Log do OCI DevOps ao centralizá-lo no módulo Logging.
moved {
  from = module.devops_gru.oci_logging_log.devops
  to   = module.logging_gru.oci_logging_log.devops[0]
}
