#
# datasource.tf
#   - Data Source global.
# 

data "external" "get_my_public_ip" {
    program = ["bash", "./scripts/get-my-publicip.sh"]
}

data "oci_objectstorage_namespace" "objectstorage_ns" {
    provider = oci.home_region
    compartment_id = var.tenancy_id
}