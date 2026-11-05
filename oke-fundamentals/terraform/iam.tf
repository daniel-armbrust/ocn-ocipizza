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
