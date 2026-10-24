#
# compute-firewall/locals.tf
#

locals {
  # Imagem Oracle Linux 8 compatível com VM.Standard.A1.Flex em GRU.
  compute_firewall_gru = {
    name     = "firewall-gru"
    image_id = "ocid1.image.oc1.sa-saopaulo-1.aaaaaaaatlmyccwaepgtojuuibmmq7k63pcppdabnvbf676e65vcsvmsofdq"
  }

  # Imagem Oracle Linux 8 compatível com VM.Standard.A1.Flex em VCP.
  compute_firewall_vcp = {
    name     = "firewall-vcp"
    image_id = "ocid1.image.oc1.sa-vinhedo-1.aaaaaaaagfwe2thy25z3qu2fdeiui72mgat7qulz7pqjrzrxupxp3beksqhq"
  }

  # Parâmetros fixos do shape ARM escolhido para o firewall.
  shape = {
    name          = "VM.Standard.A1.Flex"
    ocpus         = 2
    memory_in_gbs = 4
  }

  # O índice identifica a instância dentro da região e evita colisões de nome.
  resource_suffix = var.firewall_index == 1 ? "" : "-${var.firewall_index}"

  resource_names = {
    instance = "${local.config.name}-${var.firewall_index}"
  }

  # A instância possui somente uma VNIC na sub-rede privada do firewall.
  vnic_names = {
    firewall = {
      display_name   = "vnic-firewall-${var.region_key}${local.resource_suffix}"
      hostname_label = "firewall${local.resource_suffix}"
    }
  }

  # A única VNIC criada com a instância é a referência usada pelos outputs e
  # pelo DRG enquanto o restante da arquitetura é migrado.
  primary_vnic_id = one([
    for attachment in data.oci_core_vnic_attachments.this.vnic_attachments : attachment.vnic_id
    if attachment.subnet_id == var.subnet_ids.firewall
  ])

  # Seleciona a configuração correspondente à instância regional do módulo.
  config = var.region_key == "gru" ? local.compute_firewall_gru : local.compute_firewall_vcp
}
