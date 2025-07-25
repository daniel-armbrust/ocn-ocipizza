#
# policy.tf
#   - Políticas de autorização do serviço de IAM.
#

resource "oci_identity_dynamic_group" "dyngrp_instance" {
    provider = oci.home_region

    compartment_id = var.tenancy_id

    name = "dyngrp-instance"
    description = "Grupo dinâmico que inclui as instâncias de computação do compartimento especificado."

    matching_rule = "All {instance.compartment.id = '${var.compartment_id}'}"
}

resource "oci_identity_policy" "objectstorage_policy" {    
    provider = oci.home_region
    
    compartment_id = var.tenancy_id

    name = "objectstorage_policy"
    description = "Políticas IAM que concedem acesso ao Object Storage a partir do grupo dinâmico especificado."

    statements = [    
       "Allow dynamic-group ${oci_identity_dynamic_group.dyngrp_instance.name} to read buckets in compartment id ${var.compartment_id} where target.bucket.name='${oci_objectstorage_bucket.vcp_objectstorage_scripts-storage.name}'",
       "Allow dynamic-group ${oci_identity_dynamic_group.dyngrp_instance.name} to read objects in compartment id ${var.compartment_id} where target.bucket.name='${oci_objectstorage_bucket.vcp_objectstorage_scripts-storage.name}'",
       "Allow dynamic-group ${oci_identity_dynamic_group.dyngrp_instance.name} to read buckets in compartment id ${var.compartment_id} where target.bucket.name='${oci_objectstorage_bucket.vcp_objectstorage_scripts-storage.name}'",
       "Allow dynamic-group ${oci_identity_dynamic_group.dyngrp_instance.name} to read objects in compartment id ${var.compartment_id} where target.bucket.name='${oci_objectstorage_bucket.vcp_objectstorage_scripts-storage.name}'"
    ]
}