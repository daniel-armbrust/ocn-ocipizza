#
# devops/bootstrap/mysql/outputs.tf
#

output "build_stage_id" {
  description = "OCID do Managed Build stage de bootstrap do MySQL."
  value       = oci_devops_build_pipeline_stage.bootstrap_mysql.id
}
