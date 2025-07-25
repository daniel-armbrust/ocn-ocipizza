#
# vcp_objectstorage.tf
#   - Object Storage da região VCP. 
#

resource "oci_objectstorage_bucket" "vcp_objectstorage_scripts-storage" {
    provider = oci.vcp

    compartment_id = var.compartment_id
    namespace = local.objectstorage_ns
    name = "scripts-storage"
    access_type = "ObjectReadWithoutList"
    versioning = "Disabled"
}

resource "oci_objectstorage_object" "vcp_objectstorage_scripts-storage_rc-firewall" {
    provider = oci.vcp
    
    bucket = "scripts-storage"
    namespace = local.objectstorage_ns    
       
    object = "rc-firewall.sh"
    source = "scripts/rc-firewall.sh"
    content_type = "text/plain"

    depends_on = [oci_objectstorage_bucket.vcp_objectstorage_scripts-storage]  
}