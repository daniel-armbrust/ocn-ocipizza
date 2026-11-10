#
# iam.tf
#

# Inclui as Compute instances do compartment no Dynamic Group. Isso contempla
# os worker nodes do OKE, inclusive quando forem substituídos pelo node pool.
resource "oci_identity_dynamic_group" "oke_worker_nodes" {
  compartment_id = var.tenancy_id
  name           = "oke-fundamentals-worker-nodes"
  description    = "Worker nodes do laboratório OKE Fundamentals."
  matching_rule  = "instance.compartment.id = '${var.compartment_id}'"
}

# Restringe a leitura aos repositórios cujo nome começa com ocipizza. O verbo
# read não concede permissão para publicar ou excluir imagens no OCIR.
resource "oci_identity_policy" "oke_worker_nodes_ocir" {
  compartment_id = var.tenancy_id
  name           = "oke-fundamentals-worker-nodes-ocir"
  description    = "Permite aos worker nodes do OKE baixar imagens do OCIR."

  statements = [
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_worker_nodes.id} to read repos in tenancy where all { target.repo.name=/ocipizza\\/*/ }",
  ]
}

# Dynamic Group usado pelo OCI Native Ingress Controller com instance principal.
# O add-on é executado nos worker nodes gerenciados do cluster.
resource "oci_identity_dynamic_group" "oke_native_ingress_controller" {
  compartment_id = var.tenancy_id
  name           = "oke-fundamentals-native-ingress-controller"
  description    = "Worker nodes que executam o OCI Native Ingress Controller."
  matching_rule  = "ALL {instance.compartment.id = '${var.compartment_id}'}"
}

# Permissões oficiais necessárias para o OCI Native Ingress Controller criar e
# atualizar Load Balancers, configurar a rede e gerenciar certificados TLS.
# O escopo fica restrito ao compartment que hospeda o cluster OKE.
resource "oci_identity_policy" "oke_native_ingress_controller" {
  compartment_id = var.tenancy_id
  name           = "oke-fundamentals-native-ingress-controller"
  description    = "Permissões do OCI Native Ingress Controller no compartment do OKE."

  statements = [
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage load-balancers in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to use virtual-network-family in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage cabundles in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage cabundle-associations in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage leaf-certificates in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to read leaf-certificate-bundles in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage leaf-certificate-versions in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage certificate-associations in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to read certificate-authorities in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage certificate-authority-associations in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to read certificate-authority-bundles in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to read public-ips in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage floating-ips in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to manage waf-family in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to read cluster-family in compartment id ${var.compartment_id}",
    "Allow dynamic-group id ${oci_identity_dynamic_group.oke_native_ingress_controller.id} to use tag-namespaces in compartment id ${var.compartment_id}",
  ]
}
