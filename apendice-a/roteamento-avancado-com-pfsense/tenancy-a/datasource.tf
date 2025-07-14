#
# datasource.tf
#   - Data Source global.
# 

data "external" "get_my_public_ip" {
    program = ["bash", "./scripts/get_my_publicip.sh"]
}