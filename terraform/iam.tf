#
# iam.tf
#

# Inclui as instâncias Compute e os Container Instances do compartment que
# utilizam Instance Principals ou Resource Principals.
resource "oci_identity_dynamic_group" "ocipizza_instances" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.iam_dynamic_group_name
  description    = "Workloads do OCI Pizza autorizados a utilizar os serviços gerenciados da aplicação."
  matching_rule  = "ANY {ALL {instance.compartment.id = '${var.compartment_id}'}, ALL {resource.type = 'computecontainerinstance', resource.compartment.id = '${var.compartment_id}'}}"
}

# Autoriza os workloads a consumir os serviços gerenciados sem conceder
# permissão para alterar seus recursos de controle.
resource "oci_identity_policy" "ocipizza_instance_principals" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.iam_policy_name
  description    = "Permissões dos Instance Principals utilizados pelos workloads do OCI Pizza."

  statements = [
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read nosql-tables in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to manage nosql-rows in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read buckets in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to manage objects in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read queues in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to use queue-push in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to use queue-pull in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read secret-bundles in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to use log-content in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_instances.id} to read repos in compartment id ${var.compartment_id}",
  ]
}

# Agrupa os resource principals usados pelas conexões e pipelines do OCI
# DevOps dentro do compartment da aplicação.
resource "oci_identity_dynamic_group" "ocipizza_devops" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.devops_dynamic_group_name
  description    = "Resource Principals utilizados pelo OCI DevOps do OCI Pizza."
  matching_rule  = "ANY {ALL {resource.type = 'devopsdeploypipeline', resource.compartment.id = '${var.compartment_id}'}, ALL {resource.type = 'devopsbuildpipeline', resource.compartment.id = '${var.compartment_id}'}, ALL {resource.type = 'devopsrepository', resource.compartment.id = '${var.compartment_id}'}, ALL {resource.type = 'devopsconnection', resource.compartment.id = '${var.compartment_id}'}}"
}

# Permissões usadas para obter o código do GitHub, construir e publicar imagens
# no OCIR e realizar deployments nos clusters OKE. As permissões de Container
# Instances antecipam os deployments desses workloads pela pipeline.
resource "oci_identity_policy" "ocipizza_devops" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.devops_policy_name
  description    = "Permissões das pipelines do OCI DevOps do OCI Pizza."

  statements = [
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to manage devops-family in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to manage repos in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to manage generic-artifacts in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to read all-artifacts in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to read secret-family in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to use ons-topics in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to use cabundles in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to use subnets in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to use vnics in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to use dhcp-options in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to use network-security-groups in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to manage cluster in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to manage compute-container-instances in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to manage compute-containers in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to read nosql-tables in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to manage nosql-rows in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to read buckets in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to manage objects in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.ocipizza_devops.id} to use log-content in compartment id ${var.compartment_id}",
  ]
}

# Autoriza os serviços gerenciados da OCI a operar os recursos necessários ao
# OKE e à replicação regional do Object Storage.
resource "oci_identity_policy" "ocipizza_service_principals" {
  provider = oci.gru

  compartment_id = var.tenancy_id
  name           = var.service_principals_policy_name
  description    = "Permissões dos serviços gerenciados utilizados pelo OCI Pizza."

  statements = [
    "Allow service oke to manage private-ips in compartment id ${var.compartment_id}",
    "Allow service objectstorage-sa-saopaulo-1 to manage object-family in compartment id ${var.compartment_id}",
    "Allow service objectstorage-sa-vinhedo-1 to manage object-family in compartment id ${var.compartment_id}",
  ]
}
