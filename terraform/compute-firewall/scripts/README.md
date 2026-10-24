# Scripts do Compute Firewall

Este diretório contém os scripts executados na inicialização da instância do
firewall. Arquivos de configuração, como `squid.conf`, ficam em `../config/`.

## `configure-firewall.sh`

O script é enviado como `user_data` e executado pelo cloud-init. A instância
possui uma única VNIC privada, localizada na sub-rede do firewall.

Durante a inicialização, o script:

- desabilita o `firewalld` com `systemctl --now disable firewalld`;
- configura o SELinux em modo `permissive` durante a execução e no arquivo
  `/etc/selinux/config`;
- aplica uma regra IPv4 `MASQUERADE` na interface que possui a rota default;
- grava as regras em `/etc/sysconfig/iptables`;
- instala o próprio script em `/etc/rc.local` para reaplicar o NAT depois de
  cada reboot.

O script não configura VNICs secundárias, roteamento entre interfaces,
encaminhamento IPv6 ou NAT IPv6, pois a nova arquitetura utiliza somente uma
VNIC no firewall.
