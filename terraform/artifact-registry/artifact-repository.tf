#
# artifact-registry/artifact-repository.tf
#

# Armazena os manifests Kubernetes renderizados para a região. As versões são
# imutáveis para preservar a correspondência entre commit, build e deployment.
resource "oci_artifacts_repository" "kubernetes_manifests" {
  compartment_id  = var.compartment_id
  display_name    = local.repository_name
  description     = "Manifests Kubernetes renderizados da OCI Pizza em ${upper(var.region_key)}."
  is_immutable    = true
  repository_type = "GENERIC"
}
