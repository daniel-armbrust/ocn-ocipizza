#
# outputs.tf
#

output "iam_dynamic_group_id" {
  description = "OCID do dynamic group utilizado pelos Instance Principals da OCI Pizza."
  value       = oci_identity_dynamic_group.ocipizza_instances.id
}

output "iam_policy_id" {
  description = "OCID da policy dos Instance Principals da OCI Pizza."
  value       = oci_identity_policy.ocipizza_instance_principals.id
}

output "infrastructure_deployer_policy_id" {
  description = "OCID da policy utilizada pelo grupo executor do stack de infraestrutura."
  value       = oci_identity_policy.ocipizza_infrastructure_deployer.id
}
