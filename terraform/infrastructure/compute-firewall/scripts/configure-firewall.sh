#!/usr/bin/env bash
#
# compute-firewall/scripts/configure-firewall.sh
#
# Script executado pelo cloud-init na inicialização do firewall.
#
# Responsabilidades:
# - desabilitar o firewalld padrão do Oracle Linux;
# - configurar o SELinux em modo permissive;
# - aplicar MASQUERADE IPv4 pela única VNIC da sub-rede do firewall.
#

readonly IPTABLES_FILE="/etc/sysconfig/iptables"
readonly RC_LOCAL_FILE="/etc/rc.local"
readonly RC_LOCAL_SERVICE_FILE="/etc/systemd/system/rc-local.service"
readonly SELINUX_CONFIG_FILE="/etc/selinux/config"
readonly SYSCTL_CONFIG_FILE="/etc/sysctl.d/99-oci-pizza-firewall.conf"

log() {
  printf '[oci-pizza-firewall] %s\n' "$1"
}

fail() {
  printf '[oci-pizza-firewall] ERRO: %s\n' "$1" >&2
  exit 1
}

# Desabilita os controles padrão do Oracle Linux e mantém o SELinux permissive
# também depois de um reboot.
configure_host_security() {
  if systemctl cat firewalld.service >/dev/null 2>&1; then
    systemctl --now disable firewalld
  fi

  if command -v setenforce >/dev/null 2>&1; then
    setenforce 0 || true
  fi

  if [[ -f "$SELINUX_CONFIG_FILE" ]]; then
    if grep -q '^SELINUX=' "$SELINUX_CONFIG_FILE"; then
      sed -i 's/^SELINUX=.*/SELINUX=permissive/' "$SELINUX_CONFIG_FILE"
    else
      printf '\nSELINUX=permissive\n' >> "$SELINUX_CONFIG_FILE"
    fi
  else
    mkdir -p "$(dirname "$SELINUX_CONFIG_FILE")"
    printf 'SELINUX=permissive\n' > "$SELINUX_CONFIG_FILE"
  fi
}

# Habilita o encaminhamento IPv4 para que o firewall consiga transportar os
# pacotes recebidos pelo NLB até o Service Gateway ou o NAT Gateway. A mesma
# configuração é gravada no sysctl para permanecer ativa após reboot.
configure_ip_forwarding() {
  mkdir -p "$(dirname "$SYSCTL_CONFIG_FILE")"

  cat > "$SYSCTL_CONFIG_FILE" <<'EOF'
net.ipv4.ip_forward = 1
EOF

  sysctl --system >/dev/null
}

# Obtém a interface que possui a rota default criada pela configuração da
# VNIC primária. A mesma interface será usada para o MASQUERADE de saída.
get_default_interface() {
  ip route show default | awk 'NR == 1 {print $5; exit}'
}

# Instala o próprio script como rc.local para reaplicar o MASQUERADE depois de
# cada reboot, quando a rota default já estiver disponível.
configure_rc_local() {
  if [[ "$0" == "$RC_LOCAL_FILE" ]]; then
    return 0
  fi

  if [[ -f "$RC_LOCAL_FILE" ]]; then
    cp -p "$RC_LOCAL_FILE" "${RC_LOCAL_FILE}.oci-pizza-backup"
  fi

  install -m 0750 "$0" "$RC_LOCAL_FILE"

  cat > "$RC_LOCAL_SERVICE_FILE" <<'EOF'
[Unit]
Description=OCI Pizza firewall NAT
ConditionFileIsExecutable=/etc/rc.local
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/etc/rc.local
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable rc-local.service >/dev/null
}

set -Eeuo pipefail

command -v ip >/dev/null 2>&1 || \
  fail 'iproute é obrigatório para identificar a interface de saída.'

command -v iptables >/dev/null 2>&1 || \
  fail 'iptables é obrigatório para configurar o MASQUERADE IPv4.'

command -v iptables-save >/dev/null 2>&1 || \
  fail 'iptables-save é obrigatório para persistir a regra NAT.'

command -v systemctl >/dev/null 2>&1 || \
  fail 'systemctl é obrigatório para desabilitar o firewalld.'

if [[ "$(id -u)" -ne 0 ]]; then
  fail 'o script precisa ser executado como root.'
fi

configure_rc_local

log 'Desabilitando firewalld e configurando SELinux como permissive.'
configure_host_security

log 'Habilitando encaminhamento IPv4 para o tráfego inspecionado.'
configure_ip_forwarding

firewall_interface="$(get_default_interface)"
if [[ -z "$firewall_interface" ]]; then
  fail 'não foi possível identificar a interface com a rota default.'
fi

log "Aplicando MASQUERADE IPv4 pela interface ${firewall_interface}."
if ! iptables -t nat -C POSTROUTING -o "$firewall_interface" -j MASQUERADE \
  2>/dev/null; then
  iptables -t nat -A POSTROUTING -o "$firewall_interface" -j MASQUERADE
fi

mkdir -p "$(dirname "$IPTABLES_FILE")"
iptables-save > "$IPTABLES_FILE"

log 'Configuração do firewall concluída.'

exit 0
