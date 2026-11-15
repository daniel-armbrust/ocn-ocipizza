#
# iam.tf
#

# Os workloads da OCI Pizza utilizam Instance Principals para acessar os
# serviços gerenciados. O dynamic group inclui as instâncias Compute criadas no
# compartment da infraestrutura, incluindo os worker nodes dos clusters OKE.
resource "oci_identity_dynamic_group" "ocipizza_instances" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.iam_dynamic_group_name
  description    = "Instâncias da OCI Pizza autorizadas a utilizar os serviços gerenciados da aplicação."
  matching_rule  = "instance.compartment.id = '${var.infrastructure_compartment_id}'"
}

# A policy é criada no root compartment, mas suas permissões são limitadas ao
# compartment da infraestrutura. Os recursos de controle (tabelas, buckets e
# filas) continuam sob responsabilidade do stack; os workloads recebem apenas
# as operações necessárias em tempo de execução.
resource "oci_identity_policy" "ocipizza_instance_principals" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.iam_policy_name
  description    = "Permissões dos Instance Principals utilizados pelos workloads do OCI Pizza."

  statements = [
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read nosql-tables in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to manage nosql-rows in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read buckets in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to manage objects in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read queues in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to use queue-push in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to use queue-pull in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to use email-family in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read secret-bundles in compartment id ${var.infrastructure_compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to use log-content in compartment id ${var.infrastructure_compartment_id}",
  ]
}

# Os jobs do Resource Manager são autorizados como o usuário que os inicia. A
# policy fica no root compartment porque também contém permissões de leitura no
# escopo da tenancy, mas as permissões de gerenciamento são limitadas aos
# compartments do Resource Manager e da infraestrutura do OCI Pizza.
resource "oci_identity_policy" "ocipizza_infrastructure_deployer" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.infrastructure_deployer_policy_name
  description    = "Permissões necessárias para executar a stack de infraestrutura do OCI Pizza."

  statements = distinct([
    "Allow group id ${var.infrastructure_deployer_group_id} to manage all-resources in compartment id ${var.resource_manager_compartment_id}",
    "Allow group id ${var.infrastructure_deployer_group_id} to manage all-resources in compartment id ${var.infrastructure_compartment_id}",
  ])
}

# Estas permissões autorizam serviços gerenciados da OCI a operar os recursos
# necessários ao OKE, ao Email Delivery e à replicação do Object Storage.
resource "oci_identity_policy" "ocipizza_service_principals" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.service_principals_policy_name
  description    = "Permissões dos serviços gerenciados utilizados pelo OCI Pizza."

  statements = [
    "Allow service oke to manage private-ips in compartment id ${var.infrastructure_compartment_id}",
    "Allow service EmailDelivery to read email-configuration in tenancy",
    "Allow service objectstorage-sa-saopaulo-1 to manage object-family in compartment id ${var.infrastructure_compartment_id}",
    "Allow service objectstorage-sa-vinhedo-1 to manage object-family in compartment id ${var.infrastructure_compartment_id}",
  ]
}
