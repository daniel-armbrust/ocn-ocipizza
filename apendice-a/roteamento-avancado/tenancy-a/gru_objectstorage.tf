#
# gru_objectstorage.tf
#   - Object Storage da região GRU. 
#

resource "oci_objectstorage_bucket" "gru_objectstorage_scripts-storage" {
    provider = oci.gru

    compartment_id = var.compartment_id
    namespace = local.objectstorage_ns
    name = "scripts-storage"
    access_type = "NoPublicAccess"
    versioning = "Disabled"
}

resource "oci_objectstorage_object" "gru_objectstorage_scripts-storage_rc-firewall" {
    provider = oci.gru
    
    bucket = "scripts-storage"
    namespace = local.objectstorage_ns    
       
    object = "rc-firewall.sh"
    source = "scripts/rc-firewall.sh"
    content_type = "text/plain"

    depends_on = [oci_objectstorage_bucket.gru_objectstorage_scripts-storage]  
}