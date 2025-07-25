#!/bin/bash
#
# /etc/rc-firewall - Firewall e Policy Routing das regiões GRU e VCP.
#

# Configuração das interfaces de rede.
/usr/bin/oci-network-config configure

# Tabela de Rotas para gerenciar o roteamento de tráfego da interface 
# WAN OUTBOUND (500) para a Internet.
if [ -z "`grep internet_wan_outbound /etc/iproute2/rt_tables`" ]; then
   echo '500 internet_wan_outbound' >> /etc/iproute2/rt_tables
fi

# Tabela de Rotas para gerenciar o roteamento de tráfego da interface 
# WAN VPN (600) para a Internet.
if [ -z "`grep internet_wan_vpn /etc/iproute2/rt_tables`" ]; then
   echo '600 internet_wan_vpn' >> /etc/iproute2/rt_tables
fi

#----------------------------------#
# Obtém dados do Instance Metadata #
#----------------------------------#

# https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/gettingmetadata.htm

# Região.
region="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/region`"

# Primary VNIC.
primary_vnic_ip="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/primary-vnic-ip`"
primary_vnic_iface="`ip -o -f inet addr show | grep "$primary_vnic_ip" | awk '{print $2}'`"

# WAN Outbound.
wan_outbound_ip="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/wan-outbound-ip`"
wan_outbound_gw="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/wan-outbound-gw`"
wan_outbound_iface="`ip -o -f inet addr show | grep "$wan_outbound_ip" | awk '{print $2}'`"

# WAN VPN.
wan_vpn_ip="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/wan-vpn-ip`"
wan_vpn_gw="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/wan-vpn-gw`"
wan_vpn_iface="`ip -o -f inet addr show | grep "$wan_vpn_ip" | awk '{print $2}'`"

# VCN CIDRs (GRU e VCP).
gru_vcn_firewall_cidr="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/gru-vcn-firewall-cidr 2>/dev/null`"
gru_vcn_appl_1_cidr="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/gru-vcn-appl-1-cidr 2>/dev/null`"
gru_vcn_appl_2_cidr="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/gru-vcn-appl-2-cidr 2>/dev/null`"
vcp_vcn_firewall_cidr="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/vcp-vcn-firewall-cidr 2>/dev/null`"
vcp_vcn_appl_1_cidr="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/vcp-vcn-appl-1-cidr 2>/dev/null`"
vcp_vcn_appl_2_cidr="`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/vcp-vcn-appl-2-cidr 2>/dev/null`"

#-----------------------#
# Parâmetros do Kernel  #
#-----------------------#

echo 1 > /proc/sys/net/ipv4/ip_forward

echo 1 > /proc/sys/net/ipv4/conf/$primary_vnic_iface/log_martians
echo 1 > /proc/sys/net/ipv4/conf/$wan_outbound_iface/log_martians
echo 1 > /proc/sys/net/ipv4/conf/$wan_vpn_iface/log_martians
echo 1 > /proc/sys/net/ipv4/conf/all/log_martians
echo 1 > /proc/sys/net/ipv4/conf/default/log_martians

echo 0 > /proc/sys/net/ipv4/conf/$primary_vnic_iface/rp_filter
echo 0 > /proc/sys/net/ipv4/conf/$wan_outbound_iface/rp_filter
echo 0 > /proc/sys/net/ipv4/conf/$wan_vpn_iface/rp_filter
echo 0 > /proc/sys/net/ipv4/conf/all/rp_filter
echo 0 > /proc/sys/net/ipv4/conf/default/rp_filter

#-----------------------#
# Inicializa o IPTables #
#-----------------------#

iptables -t filter -F
iptables -t filter -X
iptables -t filter -Z

iptables -t mangle -F
iptables -t mangle -X
iptables -t mangle -Z

iptables -t nat -F
iptables -t nat -X
iptables -t nat -Z

#------------------------------------------------------=---#
# Permite acesso entre os firewalls das diferentes regiões #
#-------------------------------------------------------=--#

if [ "$region" == 'sa-saopaulo-1' ]; then

    # VCN-FIREWALL (VCP).
    # Firewall da região GRU acessa o firewall da região VCP. 
    iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
             -s $primary_vnic_ip -d $vcp_vcn_firewall_cidr -j MARK --set-mark 1000             
    iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
             -s $primary_vnic_ip -d $vcp_vcn_firewall_cidr -j RETURN
    
    iptables -t mangle -A PREROUTING -d $vcp_vcn_firewall_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -d $vcp_vcn_firewall_cidr -j RETURN       

elif [ "$region" == 'sa-vinhedo-1' ]; then

    # VCN-FIREWALL (GRU)
    # Firewall da região VCP acessa o firewall da região GRU.
    iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
             -s $primary_vnic_ip -d $gru_vcn_firewall_cidr -j MARK --set-mark 1000
    iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
             -s $primary_vnic_ip -d $gru_vcn_firewall_cidr -j RETURN

     
    iptables -t mangle -A PREROUTING -d $gru_vcn_firewall_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -d $gru_vcn_firewall_cidr -j RETURN

fi

#---------------------------------------------------------#
# Permite que o firewall tenha acesso as VCNs das regiões #
#---------------------------------------------------------#

# VCN-APPL-1 (GRU).
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d $gru_vcn_appl_1_cidr -j MARK --set-mark 1000
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d $gru_vcn_appl_1_cidr -j RETURN
    
# VCN-APPL-1 (VCP).
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d $vcp_vcn_appl_1_cidr -j MARK --set-mark 1000
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d $vcp_vcn_appl_1_cidr -j RETURN
    
# VCN-APPL-2 (GRU).
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d $gru_vcn_appl_2_cidr -j MARK --set-mark 1000
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d $gru_vcn_appl_2_cidr -j RETURN
    
# VCN-APPL-2 (VCP).
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d $vcp_vcn_appl_2_cidr -j MARK --set-mark 1000
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d $vcp_vcn_appl_2_cidr -j RETURN

#---------------------------------------------------------#
# Permite que as VCNs de aplicação acessem as VCNs de     #
# aplicação da outra região, passando pelo firewall.      #
#---------------------------------------------------------#

if [ "$region" == 'sa-saopaulo-1' ]; then

    # VCN-APPL-1 (GRU) > VCN-APPL-1 (VCP)
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $gru_vcn_appl_1_cidr -d $vcp_vcn_appl_1_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $gru_vcn_appl_1_cidr -d $vcp_vcn_appl_1_cidr -j RETURN
    
    # VCN-APPL-1 (GRU) > VCN-APPL-2 (VCP)
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $gru_vcn_appl_1_cidr -d $vcp_vcn_appl_2_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $gru_vcn_appl_1_cidr -d $vcp_vcn_appl_2_cidr -j RETURN

    # VCN-APPL-2 (GRU) > VCN-APPL-1 (VCP)
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $gru_vcn_appl_2_cidr -d $vcp_vcn_appl_1_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $gru_vcn_appl_2_cidr -d $vcp_vcn_appl_1_cidr -j RETURN
    
    # VCN-APPL-2 (GRU) > VCN-APPL-2 (VCP)
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $gru_vcn_appl_2_cidr -d $vcp_vcn_appl_2_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $gru_vcn_appl_2_cidr -d $vcp_vcn_appl_2_cidr -j RETURN

elif [ "$region" == 'sa-vinhedo-1' ]; then

    # VCN-APPL-1 (VCP) > VCN-APPL-1 (GRU)
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $vcp_vcn_appl_1_cidr -d $gru_vcn_appl_1_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $vcp_vcn_appl_1_cidr -d $gru_vcn_appl_1_cidr -j RETURN
    
    # VCN-APPL-1 (VCP) > VCN-APPL-2 (GRU)
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $vcp_vcn_appl_1_cidr -d $gru_vcn_appl_2_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $vcp_vcn_appl_1_cidr -d $gru_vcn_appl_2_cidr -j RETURN

    # VCN-APPL-2 (VCP) > VCN-APPL-1 (GRU)
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $vcp_vcn_appl_2_cidr -d $gru_vcn_appl_1_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $vcp_vcn_appl_2_cidr -d $gru_vcn_appl_1_cidr -j RETURN
    
    # VCN-APPL-2 (VCP) > VCN-APPL-2 (GRU)
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $vcp_vcn_appl_2_cidr -d $gru_vcn_appl_2_cidr -j MARK --set-mark 1000
    iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
            -s $vcp_vcn_appl_2_cidr -d $gru_vcn_appl_2_cidr -j RETURN

fi

# Policy Route das regras "marcadas" com o valor 1000.
ip rule add from $primary_vnic_ip fwmark 1000 lookup main priority 1000

#------------------------#
# Conexão com a Internet #
#------------------------#

# Evita que o range link-local seja roteado para a Internet.
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d 169.254.0.0/16 -j RETURN

# Regra de NAT da interface WAN OUTBOUND.
iptables -t nat -A POSTROUTING -o $wan_outbound_iface -j MASQUERADE

# Rota default da interface WAN OUTBOUND.
ip route add default via $wan_outbound_gw \
   dev $wan_outbound_iface table internet_wan_outbound

# Regra de NAT da interface WAN VPN.
iptables -t nat -A POSTROUTING -o $wan_vpn_iface -j MASQUERADE

# Rota default da interface WAN VPN.
ip route add default via $wan_vpn_gw \
   dev $wan_vpn_iface table internet_wan_vpn

# Permite que o firewall tenha acesso à Internet.
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d 0.0.0.0/0 -j MARK --set-mark 3000
iptables -t mangle -A OUTPUT -o $primary_vnic_iface \
         -s $primary_vnic_ip -d 0.0.0.0/0 -j RETURN

# Policy Route das regras "marcadas" com o valor 3000.
ip rule add from $primary_vnic_ip fwmark 3000 lookup internet_wan_outbound priority 3000

# Permite que as VCNs de suas respectivas regiões acessem a Internet.
if [ "$region" == 'sa-saopaulo-1' ]; then

      iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
               -s $gru_vcn_appl_1_cidr -d 0.0.0.0/0 -j MARK --set-mark 3050  
      iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
               -s $gru_vcn_appl_1_cidr -d 0.0.0.0/0 -j RETURN
    
      iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
               -s $gru_vcn_appl_2_cidr -d 0.0.0.0/0 -j MARK --set-mark 3050  
      iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
               -s $gru_vcn_appl_2_cidr -d 0.0.0.0/0 -j RETURN

elif [ "$region" == 'sa-vinhedo-1' ]; then

      iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
               -s $vcp_vcn_appl_1_cidr -d 0.0.0.0/0 -j MARK --set-mark 3050  
      iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
               -s $vcp_vcn_appl_1_cidr -d 0.0.0.0/0 -j RETURN
    
      iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
               -s $vcp_vcn_appl_2_cidr -d 0.0.0.0/0 -j MARK --set-mark 3050  
      iptables -t mangle -A PREROUTING -i $primary_vnic_iface \
               -s $vcp_vcn_appl_2_cidr -d 0.0.0.0/0 -j RETURN

fi

# Policy Route das regras "marcadas" com o valor 3050.
ip rule add fwmark 3050 table internet_wan_outbound

exit 0